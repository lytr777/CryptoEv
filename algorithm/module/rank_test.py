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
    name = "rank_test"

    def __init__(self, **kwargs):
        self.bound = kwargs["bound"]

    def test(self, x, y):
        raise NotImplementedError

    def get_rc(self, s, tl, cases=()):
        return RankCases(s, tl, cases)

    def __str__(self):
        return self.name


class MannWhitneyu(RankTest):
    def __init__(self, **kwargs):
        RankTest.__init__(self, **kwargs)

    def test(self, x, y):
        if isinstance(x, RankCases) and isinstance(y, RankCases):
            nx = x.get(y.c)
            ny = y.get(x.c)
        else:
            raise TypeError("x or y has bad type")

        ylx = self.save_mw_call(nx, ny, 'less')
        xly = self.save_mw_call(ny, nx, 'less')

        return ylx, xly

    def save_mw_call(self, x, y, alternative):
        try:
            return mannwhitneyu(x, y, alternative=alternative).pvalue
        except Exception:
            return 1.

    def __str__(self):
        return "mannwhitneyu: (%f)" % self.bound


if __name__ == '__main__':
    mw = MannWhitneyu(bound=0.05)
    best = RankCases(
        52, 5,
        [("SAT", 3), ("SAT", 3), ("SAT", 3), ("SAT", 4), ("SAT", 4), ("INDET", 5), ("INDET", 5), ("INDET", 5)]
    )
    p = RankCases(
        52, 5,
        [("SAT", 3), ("SAT", 3), ("SAT", 3), ("SAT", 4), ("SAT", 4), ("INDET", 5), ("INDET", 5), ("INDET", 5)]
    )
    print mw.test(best, p)
