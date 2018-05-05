import numpy as np

from copy import copy


def one_point_crossover(v, w):
    new_v, new_w = copy(v), copy(w)
    pos = np.random.randint(len(v))

    for i in range(pos, len(v)):
        new_v[i], new_w[i] = new_w[i], new_v[i]

    return new_v, new_w


def two_point_crossover(v, w):
    new_v, new_w = copy(v), copy(w)

    a = np.random.randint(len(new_v))
    b = np.random.randint(len(new_v))

    if a > b:
        a, b = b, a

    for i in range(a, b):
        new_v[i], new_w[i] = new_w[i], new_v[i]

    return new_v, new_w


def uniform_crossover(p):
    def __uniform_crossover(v, w):
        new_v, new_w = copy(v), copy(w)
        distribution = np.random.rand(len(new_v))

        for i in range(len(new_v)):
            if p >= distribution[i]:
                new_v[i], new_w[i] = new_w[i], new_v[i]

        return new_v, new_w

    return __uniform_crossover
