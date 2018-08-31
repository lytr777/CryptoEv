import numpy as np

from copy import copy


def neighbour_mutation(backdoor):
    new_v = copy(backdoor.get_mask())
    pos = np.random.randint(len(new_v))
    new_v[pos] = not new_v[pos]
    return backdoor.get_copy(new_v)


def scaled_uniform_mutation(c):  # bit-flip
    def __scaled_uniform_mutation(backdoor):
        new_v = copy(backdoor.get_mask())
        p = float(c) / len(new_v)
        flag = True
        while flag:
            distribution = np.random.rand(len(new_v))

            for d in distribution:
                if p >= d:
                    flag = False

        for i in range(len(new_v)):
            if p >= distribution[i]:
                new_v[i] = not new_v[i]

        return backdoor.get_copy(new_v)

    return __scaled_uniform_mutation


def swap_mutation(backdoor):
    new_v = copy(backdoor.get_mask())

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

    return backdoor.get_copy(new_v)
