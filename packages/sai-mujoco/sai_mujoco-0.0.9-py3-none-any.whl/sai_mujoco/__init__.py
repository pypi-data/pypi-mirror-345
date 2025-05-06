from gymnasium import register

register(
    id="HumanoidWalk-v0",
    entry_point="sai_mujoco.humanoid_walk:HumanoidWalkEnv",
)

register(
    id="HumanoidObstacle-v0",
    entry_point="sai_mujoco.humanoid_obstacle:HumanoidObstacleEnv",
)

register(
    id="InvertedPendulumWheel-v0",
    entry_point="sai_mujoco.inverted_pendulum_wheel:InvertedPendulumWheelEnv",
)

register(
    id="XArm7-Lift-v0",
    entry_point="sai_mujoco.xarm7_lift:XArm7LiftEnv",
)

register(
    id="FrankaGolf-v0",
    entry_point="sai_mujoco.franka_golf:FrankaGolfEnv",
)

register(
    id="FrankaGolfIK-v0",
    entry_point="sai_mujoco.franka_golf:FrankaGolfEnvIK",
)
