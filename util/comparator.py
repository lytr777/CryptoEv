from numpy import sign, count_nonzero as cnz


# max s, min value
def max_min(p1, p2):
    vs = int(sign(p1[1] - p2[1]))
    if vs != 0:
        return vs
    else:
        return cnz(p2[0]) - cnz(p1[0])
