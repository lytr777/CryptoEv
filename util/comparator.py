from numpy import sign, count_nonzero as cnz, ndarray
from model.backdoor import FixedBackdoor as FB, InextensibleBackdoor as IB, ExpandingBackdoor as EB


# max s, min value
def max_min(p1, p2):
    vs = int(sign(p1[1] - p2[1]))
    if vs != 0:
        return vs
    else:
        if isinstance(p1[0], ndarray) or isinstance(p1[0], list):
            return cnz(p2[0]) - cnz(p1[0])
        elif isinstance(p1[0], FB) or isinstance(p1[0], IB) or isinstance(p1[0], EB):
            return len(p2[0]) - len(p1[0])
