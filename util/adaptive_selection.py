import numpy as np


def percent_function(x):
    if x <= 20:  # 0.8
        return 1.2 - (x / 50.)
    elif x <= 50:  # 0.5
        return 1 - (x / 100.)
    elif x <= 100:  # 0.2
        return 0.8 - (x / 166.6666666)
    elif x <= 300:  # 0.1
        return 0.25 - (x / 2000.)
    elif x <= 500:  # 0.05
        return 0.175 - (x / 4000.)
    elif x <= 800:  # 0.02
        return 0.1 - (x / 10000.)
    else:  # 0.005
        return 0.08 - (x / 13333.3333333)


class AdaptiveFunction:
    functions = {
        # "a5_1": lambda n: 1e18 / ((n / 10.) ** (2.15 * np.sqrt(np.log(np.log(n))))),
        "a5_1": lambda n: 6e+19 / ((n / 10.) ** (2.5 * np.sqrt(np.log(np.log(n)))))
    }

    def __init__(self, min_N, max_N):
        self.min_N = min_N
        self.max_N = max_N

        self.f = percent_function
        self.last_N = min_N

    def choose_function(self, algorithm):
        self.f = self.functions[algorithm]

    def get_N(self, case):
        mask, value = case[0], case[1]

        if self.f == percent_function:
            if len(case) < 3:
                raise Exception("Missing times")

            if len(case[2]) == 0:
                return self.min_N

            k = 0.
            for status, _ in case[2]:
                if status == "SAT" or status == "UNSAT":
                    k += 1

            value = k / len(case[2])

        for n in range(self.last_N, self.max_N):
            if value >= self.f(n):
                self.last_N = n
                return n

        self.last_N = self.max_N
        return self.max_N

    def reset(self):
        self.last_N = self.min_N
