"""Environment using Gymnasium API and Multi-goal API for Franka Golf."""

import mujoco
from os import path
from typing import Optional

import numpy as np
import gymnasium as gym
from gymnasium import spaces
from gymnasium.utils.ezpickle import EzPickle

from sai_mujoco.utils.ik_controller import IKController
from sai_mujoco.franka_golf.franka_robot import FrankaRobot
from gymnasium_robotics.utils.rotations import euler2quat, quat2euler, quat2mat


class FrankaGolfEnv(gym.Env, EzPickle):
    metadata = {
        "render_modes": [
            "human",
            "rgb_array",
            "depth_array",
        ],
        "render_fps": 12,
    }

    def __init__(
        self,
        robot_model_path: str = f"{path.dirname(path.realpath(__file__))}/assets/franka_golf_model.xml",
        **kwargs,
    ):
        self.robot_model_path = robot_model_path

        self.robot_env = FrankaRobot(
            model_path=robot_model_path,
            camera_name="main_camera",
            **kwargs,
        )

        self.model = self.robot_env.model
        self.data = self.robot_env.data
        self.render_mode = self.robot_env.render_mode

        # Hide overlay if rendering in human mode
        if self.render_mode == "human":
            viewer = self.robot_env.mujoco_renderer._get_viewer("human")
            viewer._hide_menu = True

        self.golf_ball_id = self.robot_env.model_names.body_name2id["golf_ball"]
        self.golf_hole_id = self.robot_env.model_names.body_name2id["flag_assembly"]
        self.golf_club_id = self.robot_env.model_names.body_name2id["grip_link"]
        self.club_head_id = self.robot_env.model_names.body_name2id["head_link"]
        self.left_finger_id = self.robot_env.model_names.body_name2id["left_finger"]
        self.right_finger_id = self.robot_env.model_names.body_name2id["right_finger"]
        self.ee_id = self.model.site("end_effector").id

        # self._reset_keyframe()
        self._init_qpos_ctrl()

        self.robot_env.init_qpos = self.robot_env.data.qpos

        robot_obs = self.robot_env._get_obs()
        obs = self._get_obs(robot_obs)

        assert int(np.round(1.0 / self.robot_env.dt)) == self.metadata["render_fps"], (
            f"Expected value: {int(np.round(1.0 / self.robot_env.dt))}, Actual value: {self.metadata['render_fps']}"
        )

        self.action_space = self.robot_env.action_space
        self.observation_space = spaces.Box(
            -np.inf, np.inf, shape=obs.shape, dtype="float64"
        )

        EzPickle.__init__(
            self,
            **kwargs,
        )

    def compute_reward(
        self,
    ):
        """Compute the reward for the current state.

        This function implements the reward terms from the Isaac implementation:
        1. Approach the club grip
        2. Grasp the handle
        3. Approach ball to the hole
        4. Penalize actions for cosmetic reasons
        5. Penalize if the club is dropped
        6. Penalize if the ball passed the hole
        """
        # Get positions and orientations
        ee_pos = self.data.site(self.ee_id).xpos
        ee_xmat = self.data.site(self.ee_id).xmat
        ee_quat = np.zeros(4)
        mujoco.mju_mat2Quat(ee_quat, ee_xmat)

        # Get club grip position and orientation
        club_grip_pos = self.data.xpos[self.golf_club_id]
        club_grip_quat = self.data.xquat[self.golf_club_id]

        # Get ball and hole positions
        ball_pos = self.data.xpos[self.golf_ball_id]
        hole_pos = self.data.xpos[self.golf_hole_id]

        # 1. Approach the club grip
        approach_ee_club_grip_weight = 0.8
        approach_ee_club_grip = self._approach_ee_club_grip(ee_pos, club_grip_pos)

        align_ee_handle_weight = 0.5
        align_ee_handle = self._align_ee_handle(ee_quat, club_grip_quat)

        # 2. Grasp the handle
        approach_gripper_handle_weight = 5.0
        approach_gripper_handle = self._approach_gripper_handle(
            ee_pos, club_grip_pos, offset=0.04
        )

        # 4. Approach ball to the hole
        approach_ball_hole_weight = 3.0
        approach_ball_hole = self._approach_ball_hole(ball_pos, hole_pos)

        # 5. Penalize actions for cosmetic reasons
        action_rate_l2_weight = -1e-2
        action_rate_l2 = 0.0  # This would require tracking previous actions

        joint_vel_weight = -0.0001
        joint_vel = self._joint_vel_l2()

        # 6. Penalize if the club is dropped
        club_dropped_weight = -10.0
        club_dropped = self._club_dropped(club_grip_pos, minimum_height=0.25)

        # 7. Penalize if the ball passed the hole
        ball_passed_hole_weight = -10.0
        ball_passed_hole = self._ball_passed_hole(ball_pos, hole_pos)

        # Combine all rewards
        reward = (
            approach_ee_club_grip_weight * approach_ee_club_grip
            + align_ee_handle_weight * align_ee_handle
            + approach_gripper_handle_weight * approach_gripper_handle
            + approach_ball_hole_weight * approach_ball_hole
            + action_rate_l2_weight * action_rate_l2
            + joint_vel_weight * joint_vel
            + club_dropped_weight * club_dropped
            + ball_passed_hole_weight * ball_passed_hole
        )

        return reward

    def _approach_ee_club_grip(self, ee_pos, club_grip_pos):
        """Reward the robot for reaching the club grip using a steeper function for more responsive rewards."""
        target_pos = club_grip_pos
        target_pos[2] += 0.15  # Add offset for z axis
        distance = np.linalg.norm(ee_pos - target_pos)
        scale_factor = 15.0
        reward = np.exp(-scale_factor * distance)
        return reward

    def _align_ee_handle(self, ee_quat, handle_quat):
        """Reward for aligning the end-effector with the handle.

        The correct alignment is when:
        - The z direction of the gripper is aligned with the -y direction of the handle
        - The -y direction of the gripper is aligned with the x direction of the handle

        This ensures the gripper is oriented correctly to grasp the handle.
        """
        # Convert quaternions to rotation matrices
        ee_rot_mat = quat2mat(ee_quat)
        handle_mat = quat2mat(handle_quat)

        # Get current x, y, z directions of the handle
        handle_x, handle_y, handle_z = (
            handle_mat[:, 0],
            handle_mat[:, 1],
            handle_mat[:, 2],
        )

        # Get current x, y, z directions of the gripper
        ee_x, ee_y, ee_z = ee_rot_mat[:, 0], ee_rot_mat[:, 1], ee_rot_mat[:, 2]

        # Calculate alignment scores
        # For correct alignment:
        # - ee_z should be aligned with -handle_y (dot product should be close to 1)
        # - -ee_y should be aligned with handle_x (dot product should be close to 1)
        align_z = np.dot(ee_z, -handle_y)
        align_y = np.dot(-ee_y, handle_x)

        # Penalize misalignment more strongly
        # We want to reward when alignments are close to 1 and penalize when they're close to -1
        # Using a quadratic function that peaks at 1 and is negative for values less than 0
        z_reward = 2 * align_z**2 - 1 if align_z > 0 else -1
        y_reward = 2 * align_y**2 - 1 if align_y > 0 else -1

        # Combine rewards, ensuring both alignments must be positive for a good reward
        reward = z_reward * y_reward

        return reward

    def _approach_gripper_handle(self, ee_pos, handle_pos, offset=0.04):
        """Reward the robot's gripper reaching the club grip with the right pose.

        This function returns the distance of fingertips to the handle when the fingers are in a grasping orientation
        (i.e., the left finger is to the left of the handle and the right finger is to the right of the handle).
        Otherwise, it returns zero.
        """
        left_finger_pos = self.data.xpos[self.left_finger_id]
        right_finger_pos = self.data.xpos[self.right_finger_id]

        # Check if hand is in a graspable pose
        is_graspable = (right_finger_pos[1] < handle_pos[1]) & (
            left_finger_pos[1] > handle_pos[1]
        )

        is_graspable = (
            is_graspable
            & (ee_pos[2] < handle_pos[2] + 0.03)
            & (ee_pos[0] - handle_pos[0] < 0.02)
        )

        if not is_graspable:
            return 0.0

        # Compute the distance of each finger from the handle
        lfinger_dist = np.abs(left_finger_pos[1] - handle_pos[1])
        rfinger_dist = np.abs(right_finger_pos[1] - handle_pos[1])

        # Reward is proportional to how close the fingers are to the handle when in a graspable pose
        reward = is_graspable * ((offset - lfinger_dist) + (offset - rfinger_dist)) * 10
        return reward

    def _approach_ball_hole(self, ball_pos, hole_pos):
        """Reward for approaching the ball to the hole."""
        distance = np.linalg.norm(ball_pos - hole_pos)
        reward = np.exp(distance * -3.0)
        return reward

    def _joint_vel_l2(self):
        """Penalize joint velocities."""
        joint_vel = self.data.qvel[:7]  # Assuming first 7 joints are the arm joints
        return np.sum(joint_vel**2)

    def _club_dropped(self, club_grip_pos, minimum_height=0.25):
        """Penalize if the club is dropped."""
        return float(club_grip_pos[2] < minimum_height)

    def _ball_passed_hole(self, ball_pos, hole_pos):
        """Penalize if the ball passed the hole."""
        # Check if the ball has passed the hole in the x direction
        return float(ball_pos[0] < hole_pos[0] - 0.1)

    def _ball_in_hole(self, ball_pos, hole_pos):
        """Check if the ball is in the hole."""
        return np.linalg.norm(ball_pos - hole_pos) < 0.06

    def _get_obs(self, robot_obs):
        ball_xpos = self.data.xpos[self.golf_ball_id]
        hole_xpos = self.data.xpos[self.golf_hole_id]
        golf_club_xpos = self.data.xpos[self.golf_club_id]
        golf_club_quat = self.data.xquat[self.golf_club_id]

        obs = np.concatenate(
            (robot_obs, ball_xpos, hole_xpos, golf_club_xpos, golf_club_quat)
        )

        return obs

    def step(self, action):
        robot_obs, _, terminated, truncated, info = self.robot_env.step(action)
        obs = self._get_obs(robot_obs)

        reward = self.compute_reward()

        terminated = self.compute_terminated()

        return obs, reward, terminated, False, info

    def compute_terminated(self):
        ball_pos = self.data.xpos[self.golf_ball_id]
        hole_pos = self.data.xpos[self.golf_hole_id]
        club_grip_pos = self.data.xpos[self.golf_club_id]

        is_ball_in_hole = self._ball_in_hole(ball_pos, hole_pos)
        is_ball_passed_hole = self._ball_passed_hole(ball_pos, hole_pos)
        is_club_dropped = self._club_dropped(club_grip_pos, minimum_height=0.22)
        return is_ball_in_hole or is_ball_passed_hole or is_club_dropped

    def reset(self, *, seed: Optional[int] = None, **kwargs):
        robot_obs, _ = self.robot_env.reset(seed=seed)
        # self._reset_keyframe()
        self._init_qpos_ctrl()
        obs = self._get_obs(robot_obs)

        return obs, {}

    def render(self):
        return self.robot_env.render()

    def close(self):
        self.robot_env.close()

    def _reset_keyframe(self):
        init_pos_key_id = self.robot_env.model.key("init_pos").id
        mujoco.mj_resetDataKeyframe(
            self.robot_env.model, self.robot_env.data, init_pos_key_id
        )
        for _ in range(self.robot_env.frame_skip):
            mujoco.mj_step(self.robot_env.model, self.robot_env.data)

    def _init_qpos_ctrl(self):
        init_qpos = [
            0.2555,
            -0.0117,
            -0.2936,
            -2.5540,
            1.5981,
            1.4609,
            -1.7311,
            0.04,
            0.04,
        ]
        init_ctrl = [0.256, -0.00117, -0.294, -2.55, 1.6, 1.46, -1.73, 255]
        self.robot_env.data.qpos[:9] = init_qpos
        self.robot_env.data.qvel[:8] = init_ctrl
        for _ in range(self.robot_env.frame_skip):
            mujoco.mj_step(self.robot_env.model, self.robot_env.data)

    @property
    def renderer(self):
        return self.robot_env.mujoco_renderer


class FrankaGolfEnvIK(FrankaGolfEnv):
    def __init__(self, **kwargs):
        super().__init__(
            robot_model_path=f"{path.dirname(path.realpath(__file__))}/assets/franka_golf_model_IK.xml",
            **kwargs,
        )

        # Action space contains 3 delta pos + 3 delta eular rotatation of end effector + 1 gripper open/close
        self.action_space = self.robot_env.action_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(7,),
            dtype=np.float64,
        )

        self.target_mocap_name = "target"
        self.target_mocap_id = self.model.body(self.target_mocap_name).mocapid[0]

        self.ik_controller = IKController(
            self.robot_env.model,
            self.robot_env.data,
            target_mocap_name=self.target_mocap_name,
            end_effector_site_name="end_effector",
            joint_names=[
                "robot:joint1",
                "robot:joint2",
                "robot:joint3",
                "robot:joint4",
                "robot:joint5",
                "robot:joint6",
                "robot:joint7",
                "robot:finger_joint1",
                "robot:finger_joint2",
            ],
        )

    def step(self, action):
        assert action.shape == self.action_space.shape, (
            f"Action shape {action.shape} does not match expected shape {self.action_space.shape}"
        )

        action = np.clip(action, -1.0, 1.0)

        delta_pos = action[:3]
        delta_euler = action[3:6]
        gripper_action = action[6]

        mocap_pos = self.data.mocap_pos[self.target_mocap_id]
        mocap_quat = self.data.mocap_quat[self.target_mocap_id]

        mocap_pos += delta_pos

        mocap_euler = quat2euler(mocap_quat)
        mocap_euler += delta_euler
        mocap_quat = euler2quat(mocap_euler)

        self.data.mocap_pos[self.target_mocap_id] = mocap_pos
        self.data.mocap_quat[self.target_mocap_id] = mocap_quat

        ctrl = self.ik_controller.calculate_ik()
        ctrl = ctrl[: len(self.robot_env.data.ctrl)]

        gripper_ctrl_range = self.robot_env.model.actuator_ctrlrange[-1]
        if gripper_action > 0:
            ctrl[-1] = gripper_ctrl_range[1]
        else:
            ctrl[-1] = gripper_ctrl_range[0]

        self.robot_env.do_simulation(ctrl, self.robot_env.frame_skip)

        if self.render_mode == "human":
            self.render()

        robot_obs = self.robot_env._get_obs()
        obs = self._get_obs(robot_obs)

        reward = self.compute_reward()

        terminated = self.compute_terminated()

        return obs, reward, terminated, False, {}