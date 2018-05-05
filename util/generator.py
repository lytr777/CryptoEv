import numpy as np
from copy import copy


def generate_key(n):
    return np.random.randint(2, size=n)


def generate_mask(n, k):
    mask = np.zeros(n, dtype=np.int)

    choice = np.random.choice(n, k, replace=False)
    for e in choice:
        mask[e] = 1

    return mask


def generate_decomposition_key_set(base_key, indices):
    keys = [base_key]
    indices_copy = copy(indices)
    while len(indices_copy) > 0:
        index = indices_copy.pop()
        new_keys = []
        for key in keys:
            for i in range(2):
                copy_key = copy(key)
                copy_key[index] = i
                new_keys.append(copy_key)
        keys = new_keys

    return keys
