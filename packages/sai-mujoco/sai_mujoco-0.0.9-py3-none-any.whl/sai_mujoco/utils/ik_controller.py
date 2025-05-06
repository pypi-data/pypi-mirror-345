import mujoco
import numpy as np


class IKController:
    def __init__(
        self,
        model: mujoco.MjModel,
        data: mujoco.MjData,
        target_mocap_name: str,
        end_effector_site_name: str,
        joint_names: list[str],
    ):
        self.model = model
        self.data = data

        self.target_mocap_name = target_mocap_name
        self.end_effector_site_name = end_effector_site_name
        self.joint_names = joint_names

        # Integration timestep in seconds. This corresponds to the amount of time the joint
        # velocities will be integrated for to obtain the desired joint positions.
        self.integration_dt: float = 0.1

        # Damping term for the pseudoinverse. This is used to prevent joint velocities from
        # becoming too large when the Jacobian is close to singular.
        self.damping: float = 1e-4

        # Gains for the twist computation. These should be between 0 and 1. 0 means no
        # movement, 1 means move the end-effector to the target in one integration step.
        self.Kpos: float = 0.95
        self.Kori: float = 0.95

        # Whether to enable gravity compensation.
        self.gravity_compensation: bool = True

        # Simulation timestep in seconds.
        self.dt: float = 0.002

        # Nullspace P gain.
        self.Kn = np.asarray([10.0, 10.0, 10.0, 10.0, 5.0, 5.0, 5.0, 0.0, 0.0])

        # Maximum allowable joint velocity in rad/s.
        self.max_angvel: float = 0.785

        # Enable gravity compensation. Set to 0.0 to disable.
        self.model.body_gravcomp[:] = float(self.gravity_compensation)
        self.model.opt.timestep = self.dt

        # End-effector site we wish to control.
        self.site_id = self.model.site(self.end_effector_site_name).id

        # Get the dof and actuator ids for the joints we wish to control. These are copied
        # from the XML file. Feel free to comment out some joints to see the effect on
        # the controller.
        self.dof_ids = np.array(
            [self.model.joint(name).id for name in self.joint_names]
        )

        self.q0 = self.data.qpos.copy()[self.dof_ids]

        # Mocap body we will control with our mouse.
        self.mocap_name = target_mocap_name
        self.mocap_id = self.model.body(self.mocap_name).mocapid[0]

        # Pre-allocate numpy arrays.
        self.diag = self.damping * np.eye(6)
        self.eye = np.eye(len(self.dof_ids))
        self.twist = np.zeros(6)
        self.site_quat = np.zeros(4)
        self.site_quat_conj = np.zeros(4)
        self.error_quat = np.zeros(4)

    def calculate_ik(self):
        # Spatial velocity (aka twist).
        dx = self.data.mocap_pos[self.mocap_id] - self.data.site(self.site_id).xpos
        self.twist[:3] = self.Kpos * dx / self.integration_dt
        mujoco.mju_mat2Quat(self.site_quat, self.data.site(self.site_id).xmat)
        mujoco.mju_negQuat(self.site_quat_conj, self.site_quat)
        mujoco.mju_mulQuat(
            self.error_quat,
            self.data.mocap_quat[self.mocap_id],
            self.site_quat_conj,
        )
        mujoco.mju_quat2Vel(self.twist[3:], self.error_quat, 1.0)
        self.twist[3:] *= self.Kori / self.integration_dt

        # Jacobian.
        jac = np.zeros((6, self.model.nv))
        mujoco.mj_jacSite(self.model, self.data, jac[:3], jac[3:], self.site_id)

        jac = jac[:, self.dof_ids]

        # Damped least squares.
        dq = jac.T @ np.linalg.solve(jac @ jac.T + self.diag, self.twist)

        # Nullspace control biasing joint velocities towards the home configuration.
        dq += (self.eye - np.linalg.pinv(jac) @ jac) @ (
            self.Kn * (self.q0 - self.data.qpos[self.dof_ids])
        )

        # Clamp maximum joint velocity.
        dq_abs_max = np.abs(dq).max()
        if dq_abs_max > self.max_angvel:
            dq *= self.max_angvel / dq_abs_max

        # Integrate joint velocities to obtain joint positions.
        q_des = self.data.qpos.copy()[self.dof_ids] + dq * self.integration_dt
        np.clip(
            a=q_des,
            a_min=self.model.jnt_range.T[0, self.dof_ids],
            a_max=self.model.jnt_range.T[1, self.dof_ids],
            out=q_des,
        )

        return q_des
