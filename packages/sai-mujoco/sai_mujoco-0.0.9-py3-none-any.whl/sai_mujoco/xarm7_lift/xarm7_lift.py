import os

import gymnasium as gym
import numpy as np
import mujoco

from gymnasium import utils
from gymnasium.envs.mujoco.mujoco_env import MujocoEnv

from ..utils.sai_mujoco_base import SaiMujocoBase

class XArm7LiftEnv(MujocoEnv, utils.EzPickle, SaiMujocoBase):
    # Robot: https://www.ufactory.cc/product-page/ufactory-xarm-7/
    metadata = {
        "render_modes": [
            "human",
            "rgb_array",
            "depth_array",
        ],
        "render_fps": 167,
    }
    def __init__(self, show_overlay: bool = False, **kwargs):
        utils.EzPickle.__init__(self, **kwargs)
        # Gym Spaces
        observation_space = gym.spaces.Box(-np.inf, np.inf, shape=(314,), dtype=np.float64)

        MujocoEnv.__init__(
            self,
            os.path.join(
                os.path.dirname(__file__), "assets", "scene.xml"
            ),
            3,
            observation_space=observation_space,
            default_camera_config={
                "trackbodyid": 0,
                "distance": 3,
            },
            **kwargs,
        )

        self._toggle_overlay(show_overlay, kwargs["render_mode"])
        self.total_steps = 1000
        self.proximity = None

    def _get_cube_pos(self):
        cube_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, "box")
        return self.data.xpos[cube_id]

    def _get_ee_pos(self):
        ee_site_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_SITE, "ee_site")
        return self.data.site_xpos[ee_site_id]    

    def _get_obs(self):
        obs = np.concatenate(
            [
                self.data.qpos.flat, # position of each joint
                self.data.qvel.flat, # velocity of each joint
                self.data.cinert.flat, # center of mass - based body inertia and mass
                self.data.cvel.flat, # center of mass - based velocity
                self.data.qfrc_actuator.flat, # net unconstrained force,
                self._get_cube_pos() # position of the cube
            ]
        )
        return obs

    def _get_info(self):
        info = {
            "pos": self.data.xpos[1],
            "rot": self.data.xquat[1]
        }
        return info

    def reset(self, seed=None, options=None):
        # give the random reset a try after..
        super().reset(seed=None)
        mujoco.mj_resetData(self.model, self.data)
        self.step_count = 0
        self.done = False
        return self._get_obs(), self._get_info()

    def reset_model(self):
        pass

    def get_proximity_reward(self):
        proximity_reward = 0
        new_proximity = abs(np.mean(self._get_ee_pos() - self._get_cube_pos()))
        if self.proximity is not None:
            proximity_reward = self.proximity - new_proximity
        self.proximity = new_proximity
        return proximity_reward

    def get_lift_reward(self):
        cube_pos_z = self._get_cube_pos()[1]
        return cube_pos_z

    def get_reward(self):
        return self.get_proximity_reward() + self.get_lift_reward()

    def step(self, action):
        #rescale action
        if self.rescale_bool:
            action = self._rescale_action(action)

        # map to -1 to 1
        self.data.ctrl = action

        for i in range(3):
            mujoco.mj_step(self.model, self.data)

        observation = self._get_obs()
        info = self._get_info()

        # Reward function
        reward = self.get_reward()
        self.step_count += 1

        # Success condition
        success = self._get_cube_pos()[1] >= 0.5
        if success:
            reward += 1

        # Episode ending
        if (self.step_count == self.total_steps or success):
            self.done = True

        return observation, reward, self.done, False, info
