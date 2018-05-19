import numpy as np


class AdaptiveFunction:
    functions = {
        "a5_1": lambda n: 1e18 / ((n / 10.) ** (2.15 * np.sqrt(np.log(np.log(n)))))
    }

    def __init__(self, min_N, max_N):
        self.min_N = min_N
        self.max_N = max_N

        self.f = None
        self.last_N = min_N

    def choose_function(self, algorithm):
        self.f = self.functions[algorithm]

    def get_N(self, case):
        mask, value = case
        for n in range(self.last_N, self.max_N):
            if value > self.f(n + 1):
                self.last_N = n
                return n

        self.last_N = self.max_N
        return self.max_N
