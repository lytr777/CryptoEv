from numpy import sign, count_nonzero as cnz, ndarray
from model.backdoor import Backdoor, FixedBackdoor as FB


class Comparator:
    name = "comparator"
    
    def __init__(self, **kwargs):
        pass

    def compare(self, p1, p2):
        raise NotImplementedError

    def __str__(self):
        return self.name


class MaxMin(Comparator):
    # max s, min value
    def compare(self, p1, p2):
        try:
            vs = int(sign(p1[1] - p2[1]))
        except ValueError:
            vs = 0

        if vs != 0:
            return vs
        else:
            if isinstance(p1[0], ndarray) or isinstance(p1[0], list):
                return cnz(p2[0]) - cnz(p1[0])
            elif isinstance(p1[0], FB) or isinstance(p1[0], Backdoor):
                return len(p2[0]) - len(p1[0])
