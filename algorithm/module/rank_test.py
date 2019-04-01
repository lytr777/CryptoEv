from scipy.stats import mannwhitneyu


class RankCases:
    def __init__(self, s, tl, cases=()):
        self.c = 2 ** s
        self.tl = tl
        self.cases = list(cases)

    def __len__(self):
        return len(self.cases)

    def __str__(self):
        s = '['
        for case in self.cases:
            s += '%s, ' % str(case)
        return '%s]' % s[:-2]

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

    def get_2(self, cmp_c):
        min_c = min(self.c, cmp_c)
        bound = self.tl * min_c

        ind_times = []
        det_times = []
        for case in self.cases:
            if case[0] == "SAT" or case[0] == "UNSAT":
                rank = self.c * float(case[1])
                if rank < bound:
                    det_times.append(rank)
                else:
                    ind_times.append(bound)
            else:
                ind_times.append(bound)

        return det_times, ind_times


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


class Fisher(RankTest):
    def q(self, p, t, x):
        s, z = 0.0, 1.0
        i = 0
        while i <= x:
            s = s * (1 - p) + z
            z = z * p * (t - i) / (i + 1)
            i += 1
        while i <= t:
            s *= 1 - p
            i += 1

        return s

    def test(self, x, y):
        if isinstance(x, RankCases) and isinstance(y, RankCases):
            xdt, xit = x.get_2(y.c)
            ydt, yit = y.get_2(x.c)
        else:
            raise TypeError("x or y has bad type")

        p1, p2 = float(len(xdt)), float(len(ydt))
        n1, n2 = float(len(xit)), float(len(yit))
        if p1 + n1 == 0 or p2 + n2 == 0:
            return 1., 1.

        if p1 * (p2 + n2) > p2 * (p1 + n1):
            pvalue = lambda z: (z, 1 - z)
            p1, p2 = p2, p1
            n1, n2 = n2, n1
        else:
            pvalue = lambda z: (1 - z, z)

        def measure(p):
            return self.q(p, p1 + n1, p1) * self.q(1 - p, n2 + p2, n2)

        def ternary(l, r, iterations):
            if iterations == 0:
                return (l + r) / 2

            ll = (l + l + r) / 3
            llv = measure(ll)
            rr = (l + r + r) / 3
            rrv = measure(rr)

            if llv > rrv:
                return ternary(l, rr, iterations - 1)
            else:
                return ternary(ll, r, iterations - 1)

        prob = ternary(p1 / (p1 + n1), p2 / (p2 + n2), 50)
        return pvalue(measure(prob))

    def __str__(self):
        return "fisher: (%f)" % self.bound


if __name__ == '__main__':
    mw = MannWhitneyu(bound=0.05)
    fs = Fisher(bound=0.05)
    best = RankCases(
        51, 5,
        [("SAT", 3), ("SAT", 3), ("SAT", 3), ("SAT", 3), ("SAT", 4), ("INDET", 5), ("INDET", 5), ("INDET", 5), ("SAT", 3), ("SAT", 3), ("SAT", 3), ("SAT", 3), ("SAT", 4), ("INDET", 5), ("INDET", 5), ("INDET", 5)]
    )
    pp = RankCases(
        52, 5,
        [("SAT", 4), ("SAT", 3), ("SAT", 3), ("SAT", 4), ("SAT", 4), ("INDET", 5), ("INDET", 5), ("INDET", 5)]
    )
    print best.get_2(pp.c)
    print pp.get_2(best.c)
    print mw.test(best, pp)
    print fs.test(best, pp)
