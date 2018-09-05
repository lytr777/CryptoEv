import numpy as np

from copy import copy


def one_point_crossover(b1, b2):
    new_v = copy(b1.get_mask())
    new_w = copy(b2.get_mask())

    pos = np.random.randint(len(new_v))

    for i in range(pos, len(new_v)):
        new_v[i], new_w[i] = new_w[i], new_v[i]

    return b1.get_copy(new_v), b2.get_copy(new_w)


def two_point_crossover(b1, b2):
    new_v = copy(b1.get_mask())
    new_w = copy(b2.get_mask())

    a = np.random.randint(len(new_v))
    b = np.random.randint(len(new_v))

    if a > b:
        a, b = b, a

    for i in range(a, b):
        new_v[i], new_w[i] = new_w[i], new_v[i]

    return b1.get_copy(new_v), b2.get_copy(new_w)


def uniform_crossover(p):
    def __uniform_crossover(b1, b2):
        new_v = copy(b1.get_mask())
        new_w = copy(b2.get_mask())
        distribution = np.random.rand(len(new_v))

        for i in range(len(new_v)):
            if p >= distribution[i]:
                new_v[i], new_w[i] = new_w[i], new_v[i]

        return b1.get_copy(new_v), b2.get_copy(new_w)

    return __uniform_crossover
