import numpy as np

class SaiMujocoBase:
    rescale_bool = False

    def set_rescale_bool(self, rescale_bool):
        self.rescale_bool = rescale_bool

    def _rescale_action(self, action):
        expected_bounds = [-1, 1]
        action_percent = (action - expected_bounds[0]) / (expected_bounds[1] - expected_bounds[0])
        bounded_percent = np.minimum(np.maximum(action_percent, 0), 1)
        return self.action_space.low + (self.action_space.high - self.action_space.low) * bounded_percent

    def _toggle_overlay(self, show_overlay, render_mode):
        if render_mode == "human":
            if self.mujoco_renderer.viewer is None:
                self.mujoco_renderer._get_viewer(render_mode=render_mode)
            self.mujoco_renderer.viewer._hide_menu = not show_overlay