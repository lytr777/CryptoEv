import math
import numpy as np

from scipy.stats import mannwhitneyu


class RankCases:
    def __init__(self, s, tl, cases=()):
        self.c = 2 ** s
        self.tl = tl
        self.cases = list(cases)

    def __len__(self):
        return len(self.cases)

    def extend(self, cases):
        self.cases.extend(cases)

    def get(self, cmp_c):
        min_c = min(self.c, cmp_c)

        ind_times = []
        det_times = []
        for case in self.cases:
            if case[0] == "SAT" or case[0] == "UNSAT":
                det_times.append(case[1])
            else:
                ind_times.append(case[1])

        bound = self.tl * min_c
        res = []
        for time in det_times:
            rank = self.c * float(time)
            if rank < bound:
                res.append(rank)
            else:
                res.append(bound)

        res.extend([bound] * len(ind_times))
        assert len(res) == len(self.cases)
        return res


class RankTest:
    def __init__(self, **kwargs):
        self.bound = kwargs["bound"]

    def test(self, x, y):
        raise NotImplementedError

    def get_rc(self, s, tl, cases=()):
        return RankCases(s, tl, cases)


class MannWhitneyu(RankTest):
    def __init__(self, **kwargs):
        RankTest.__init__(self, **kwargs)

    def test(self, x, y):
        if isinstance(x, RankCases) and isinstance(y, RankCases):
            nx = x.get(y.c)
            ny = y.get(x.c)
        else:
            raise TypeError("x or y has bad type")

        ylx = mannwhitneyu(nx, ny, alternative='less')
        xly = mannwhitneyu(ny, nx, alternative='less')

        return ylx.pvalue, xly.pvalue


if __name__ == '__main__':
    mw = MannWhitneyu(bound=0.05)
    best = RankCases(
        52, 5,
        [("SAT", 1), ("SAT", 1), ("SAT", 1), ("SAT", 1.5), ("SAT", 1.5), ("SAT", 2), ("SAT", 2), ("SAT", 2)]
    )
    p = RankCases(
        51, 5,
        [("SAT", 3), ("SAT", 3), ("SAT", 3), ("SAT", 4), ("SAT", 4), ("INDET", 5), ("INDET", 5), ("INDET", 5)]
    )
    print mw.test(best, p)

    # ll = [157495, 164401, 184360, 204267, 208558, 223342, 229140, 233809, 218322, 203603, 199431, 199868, 203597, 204068, 199720, 184000, 173700, 169432]
    # m = float(sum(ll)) / len(ll)
    # d = sum([(l - m) ** 2 for l in ll]) / len(ll)
    # s = math.sqrt(d)
    # m /= 365.
    # s /= math.sqrt(365.)
    # print m, s
    #
    # s1 = 200000
    # s2 = 250000
    #
    # print (s2 - m * 365.) / math.sqrt(365.) / s
    # print (s1 - m * 365.) / math.sqrt(365.) / s

    d = [[('SAT', 0.068289), ('SAT', 0.072364), ('SAT', 0.072588), ('SAT', 0.073619), ('SAT', 0.069799),
          ('SAT', 0.073192), ('SAT', 0.072556), ('SAT', 0.074155), ('SAT', 0.075858), ('SAT', 0.073222)],
         [1, ('SAT', 0.071147), ('SAT', 0.073736), ('SAT', 0.074416), ('SAT', 0.074456), ('SAT', 0.073514),
          ('SAT', 0.074892), ('SAT', 0.072999), ('SAT', 0.072438), ('SAT', 0.071944), ('SAT', 0.073591)]]

    c = [[('SAT', 0.069824), ('SAT', 0.071318), ('SAT', 0.071895), ('SAT', 0.071379), ('SAT', 0.070181),
          ('SAT', 0.070978), ('SAT', 0.071567), ('SAT', 0.072602), ('SAT', 0.047508), ('SAT', 0.047815)],
         [('SAT', 0.072317), ('SAT', 0.072877), ('SAT', 0.072117), ('SAT', 0.072711), ('SAT', 0.071857),
          ('SAT', 0.073404), ('SAT', 0.072669), ('SAT', 0.073246), ('SAT', 0.047248), ('SAT', 0.045793)]]

    print np.concatenate(c)
