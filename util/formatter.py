import numpy as np


def format_array(array, mask=()):
    s = ""
    for i in range(len(array)):
        s += "_" if len(mask) > i and mask[i] == 0 else "%d" % array[i]
    s += "(%d)" % np.count_nonzero(array)
    return s


def format_to_array(s):
    s = s.split('(')[0]
    array = []
    for c in s:
        array.append(int(c))

    return np.array(array)
