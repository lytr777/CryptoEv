options = [
    {
        'param': '-luby',
        'type': 'bool',
        True: '-luby',
        False: '-no-luby',
        'default': True
    },
    {
        'param': '-rnd-init',
        'type': 'bool',
        True: '-rnd-init',
        False: '-no-rnd-init',
        'default': False
    },
    {
        'param': '-gc-frac',
        'type': 'double',
        'min': 0,
        'max': 'inf',
        'default': 0.2
    },
    {
        'param': '-rinc',
        'type': 'double',
        'min': 1,
        'max': 'inf',
        'default': 2
    },
    {
        'param': '-var-decay',
        'type': 'double',
        'min': 0,
        'max': 1,
        'default': 0.95
    },
    {
        'param': '-cla-decay',
        'type': 'double',
        'min': 0,
        'max': 1,
        'default': 0.999
    },
    {
        'param': '-rnd-freq',
        'type': 'double',
        'min': 0,
        'max': 1,
        'default': 0
    },
    {
        'param': '-rnd-seed',
        'type': 'double',
        'min': 0,
        'max': 'inf',
        'default': 9.16483e+07
    },
    {
        'param': '-phase-saving',
        'type': 'int32',
        'min': 0,
        'max': 2,
        'default': 2
    },
    {
        'param': '-ccmin-mode',
        'type': 'int32',
        'min': 0,
        'max': 2,
        'default': 2
    },
    {
        'param': '-rfirst',
        'type': 'int32',
        'min': 0,
        'max': 'imax',
        'default': 100
    },
]
