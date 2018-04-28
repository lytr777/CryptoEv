import numpy as np


def format_array(array):
    s = ""
    for a in array:
        s += "%d" % a
    s += "(%d)" % np.count_nonzero(array)
    return s


def format_to_array(s):
    s = s.split('(')[0]
    array = []
    for c in s:
        array.append(int(c))

    return np.array(array)
