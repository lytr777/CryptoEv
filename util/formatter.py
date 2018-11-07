import numpy as np


def format_to_array(s):
    s = s.split('(')[0]
    array = []
    for c in s:
        array.append(int(c))

    return np.array(array)
