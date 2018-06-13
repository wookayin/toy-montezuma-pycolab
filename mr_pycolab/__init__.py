from gym.envs.registration import register

register(
    id='ToyMontezumaRevenge-v0',
    entry_point='mr_pycolab.toy_montezuma:ToyMontezumaRevengeEnv',
    timestep_limit=10000,
    kwargs=dict(
    ),
    nondeterministic = False,
)
