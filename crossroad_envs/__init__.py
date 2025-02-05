from gymnasium.envs.registration import register

register(
    id="CrossRoad",
    entry_point="crossroad_envs.envs:CrossRoad",
)
