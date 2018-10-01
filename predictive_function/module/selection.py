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


class AdaptiveFunction:
    def __init__(self, **kwargs):
        self.min_N = kwargs["min_N"]
        self.max_N = kwargs["max_N"]

        self.f = percent_function
        self.last_N = self.min_N

    def get_N(self, case=None):
        if case is not None:
            self.correct_by(case)
        return self.last_N

    def correct_by(self, case):
        if len(case) < 3:
            raise Exception("Missing times")

        if len(case[2]) == 0:
            return

        k = 0.
        for status, _ in case[2]:
            if status == "SAT" or status == "UNSAT":
                k += 1

        value = k / len(case[2])
        for n in range(self.last_N, self.max_N):
            if value >= self.f(n):
                self.last_N = n
                return

        self.last_N = self.max_N

    def reset(self):
        self.last_N = self.min_N
        return self.min_N


class ConstSelection:
    def __init__(self, **kwargs):
        self.value = kwargs["value"]

    def get_N(self, case=None):
        return self.value

    def correct_by(self, case):
        pass

    def reset(self):
        pass
