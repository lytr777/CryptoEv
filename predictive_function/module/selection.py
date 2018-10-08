def percent_function(x):
    if x <= 20:  # 0.8
        return 1.2 - (x / 50.)
    elif x <= 50:  # 0.5
        return 1 - (x / 100.)
    elif x <= 100:  # 0.2
        return 0.8 - (x * 3 / 500.)
    elif x <= 300:  # 0.1
        return 0.25 - (x / 2000.)
    elif x <= 500:  # 0.05
        return 0.175 - (x / 4000.)
    elif x <= 800:  # 0.02
        return 0.1 - (x / 10000.)
    else:  # 0.005
        return 0.08 - (x * 3 / 40000.)


class Selection:
    name = "selection"

    def __init__(self, **kwargs):
        self.rank = 0
        self.size = 1

    def set_mpi_sett(self, size, rank):
        self.size = size
        self.rank = rank

    def get_N(self, case):
        raise NotImplementedError

    def split_selection(self, value):
        N = int(float(value) / self.size)
        remainder = value - N * self.size
        N += 1 if remainder > self.rank else 0
        return N

    def correct_by(self, case):
        raise NotImplementedError

    def __str__(self):
        return self.name


class AdaptiveFunction(Selection):
    def __init__(self, **kwargs):
        Selection.__init__(self, **kwargs)
        self.min_N = kwargs["min_N"]
        self.max_N = kwargs["max_N"]

        self.f = percent_function
        self.last_N = self.min_N

    def get_N(self, case=None):
        if case is not None:
            self.correct_by(case)
        return self.split_selection(self.last_N)

    def correct_by(self, case):
        if len(case) < 3:
            raise Exception("Missing times")

        if len(case[2]) == 0:
            return

        old_N, k = self.last_N, 0.
        for status, _ in case[2]:
            if status == "SAT" or status == "UNSAT":
                k += 1

        value = k / len(case[2])
        for n in range(self.last_N, self.max_N):
            if value >= self.f(n):
                self.last_N = n
                return old_N, self.last_N

        self.last_N = self.max_N
        return old_N, self.last_N

    def reset(self):
        self.last_N = self.min_N
        return self.min_N

    def __str__(self):
        return "adaptive from %d to %d" % (self.min_N, self.max_N)


class ConstSelection(Selection):
    def __init__(self, **kwargs):
        Selection.__init__(self, **kwargs)
        self.value = kwargs["value"]

    def get_N(self, case=None):
        return self.split_selection(self.value)

    def correct_by(self, case):
        return self.value

    def reset(self):
        pass

    def __str__(self):
        return "const (%d)" % self.value
