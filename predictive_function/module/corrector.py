import numpy as np

from key_generators.key_generator import KeyGenerator

sat_statuses = ["SATISFIABLE", "SAT"]
unsat_statuses = ["UNSATISFIABLE", "UNSAT"]
dis_statuses = ["DISCARDED", "DIS"]


def check_sat(status):
    for sat_status in sat_statuses:
        if sat_status == status:
            return True
    return False


def check_unsat(status):
    for unsat_status in unsat_statuses:
        if unsat_status == status:
            return True
    return False


def get_status(case):
    if isinstance(case, tuple):
        return case[0]
    elif isinstance(case, np.ndarray) or isinstance(case, list):
        return case[0]
    elif isinstance(case, KeyGenerator):
        return case.status


def get_time(case):
    if isinstance(case, tuple):
        return case[1]
    elif isinstance(case, np.ndarray) or isinstance(case, list):
        return float(case[1])
    elif isinstance(case, KeyGenerator):
        return case.time


class Corrector:
    name = "corrector"

    def __init__(self, **kwargs):
        self.lower_bound = kwargs["lower_bound"]

    def correct(self, cases, tl, **kwargs):
        raise NotImplementedError

    @staticmethod
    def choose_best_tl(min_tl, det_times, ind_times):
        exactly, perhaps = [], []
        for time in det_times:
            if time <= min_tl:
                exactly.append(time)
            else:
                perhaps.append(time)

        if len(perhaps) == 0:
            return min_tl

        perhaps.sort()
        if len(exactly) == 0:
            exactly.append(perhaps[0])
            perhaps.pop(0)

        n = len(det_times) + len(ind_times)
        best = (min_tl, min_tl * n / len(exactly))

        for i in range(len(perhaps)):
            value = perhaps[i] * n / (len(exactly) + i + 1)
            if value <= best[1]:
                best = (perhaps[i], value)

        return best[0]

    def __str__(self):
        return self.name


class MassCorrector(Corrector):
    def __init__(self, **kwargs):
        Corrector.__init__(self, **kwargs)
        self.coef = kwargs["coef"] if "coef" in kwargs else 1

    def correct(self, cases, tl, **kwargs):
        coef = kwargs["coef"] if "coef" in kwargs else self.coef
        det_times, ind_times = [], []

        for case in cases:
            if check_sat(get_status(case)) or check_unsat(get_status(case)):
                det_times.append(get_time(case))
            else:
                ind_times.append(tl)

        if len(det_times) == 0:
            return tl, 0

        time_sum = 0.
        for dt in det_times:
            time_sum += dt * coef
        for it in ind_times:
            time_sum += it

        new_tl = time_sum / (coef * len(det_times) + len(ind_times))
        new_tl = max(self.lower_bound, new_tl)
        best_tl = self.choose_best_tl(new_tl, det_times, ind_times)

        dis_count = 0
        for i in range(len(cases)):
            if check_sat(get_status(cases[i])) and get_time(cases[i]) > best_tl:
                dis_count += 1

        return best_tl, dis_count


class MaxCorrector(Corrector):
    def correct(self, cases, tl, **kwargs):
        min_tl = self.lower_bound
        for case in cases:
            if check_sat(get_status(case)) or check_unsat(get_status(case)):
                min_tl = max(get_time(case), min_tl)

        return min_tl, 0


class RulerCorrector(Corrector):
    def correct(self, cases, tl, **kwargs):
        det_times, ind_times = [], []
        for case in cases:
            if check_sat(get_status(case)) or check_unsat(get_status(case)):
                det_times.append(get_time(case))
            else:
                ind_times.append(tl)

        if len(det_times) == 0:
            return tl, 0

        best_tl = self.choose_best_tl(self.lower_bound, det_times, ind_times)

        dis_count = 0
        for i in range(len(cases)):
            if check_sat(get_status(cases[i])) and get_time(cases[i]) > best_tl:
                dis_count += 1

        return best_tl, dis_count
