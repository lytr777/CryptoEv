import numpy as np

from copy import copy


def neighbour_mutation(v):
    new_v = copy(v)
    pos = np.random.randint(len(new_v))
    new_v[pos] = not new_v[pos]
    return new_v


def scaled_uniform_mutation(c):  # bit-flip
    def __scaled_uniform_mutation(v):
        new_v = copy(v)
        distribution = np.random.rand(len(new_v))
        p = float(c) / len(v)

        for i in range(len(new_v)):
            if p >= distribution[i]:
                new_v[i] = not new_v[i]

        return new_v

    return __scaled_uniform_mutation

def swap_mutation(v):
    new_v = copy(v)

    zero_indices = []
    nonzero_indices = []
    for i in range(len(new_v)):
        if new_v[i] == 0:
            zero_indices.append(i)
        else:
            nonzero_indices.append(i)

    zero_pos = np.random.randint(len(zero_indices))
    nonzero_pos = np.random.randint(len(nonzero_indices))

    new_v[zero_indices[zero_pos]] = not new_v[zero_indices[zero_pos]]
    new_v[nonzero_indices[nonzero_pos]] = not new_v[nonzero_indices[nonzero_pos]]

    return new_v
