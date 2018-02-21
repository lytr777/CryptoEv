import numpy as np

from copy import copy
from util import generator


def neighbour_mutation(vector):
    new_vector = copy(vector)
    pos = np.random.randint(len(new_vector))
    new_vector[pos] = not new_vector[pos]
    return new_vector


def normally_mutation(vector):
    new_vector = copy(vector)
    distribution = generator.generate_distribution(len(new_vector))
    p = 1. / len(vector)

    for i in range(len(new_vector)):
        if p >= distribution[i]:
            new_vector[i] = not new_vector[i]

    return new_vector


def scaled_mutation(c, vector):
    new_vector = copy(vector)
    distribution = generator.generate_distribution(len(new_vector))
    p = float(c) / len(vector)

    for i in range(len(new_vector)):
        if p >= distribution[i]:
            new_vector[i] = not new_vector[i]

    return new_vector


def zero_mutation(vector, s):
    nonzero = np.count_nonzero(vector)
    if nonzero >= s:
        return

    k = s - nonzero
    offset = min(np.random.randint(2 * k) + k, nonzero)

    zero_indices = []
    for i in range(len(vector)):
        if vector[i] == 0:
            zero_indices.append(i)

    choice = np.random.choice(len(zero_indices), offset, replace=False)
    for e in choice:
        vector[zero_indices[e]] = not vector[zero_indices[e]]


def swap_mutation(vector):
    new_vector = copy(vector)

    zero_indices = []
    nonzero_indices = []
    for i in range(len(new_vector)):
        if new_vector[i] == 0:
            zero_indices.append(i)
        else:
            nonzero_indices.append(i)

    zero_pos = np.random.randint(len(zero_indices))
    nonzero_pos = np.random.randint(len(nonzero_indices))

    new_vector[zero_indices[zero_pos]] = not new_vector[zero_indices[zero_pos]]
    new_vector[nonzero_indices[nonzero_pos]] = not new_vector[nonzero_indices[nonzero_pos]]

    return new_vector
