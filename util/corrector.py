from key_generators.key_generator import KeyGenerator

sat_statuses = ["SATISFIABLE", "SAT"]
unsat_statuses = ["UNSATISFIABLE", "UNSAT"]
dis_statuses = ["DISCARDED", "DIS"]


def mass_corrector(cases, tl):
    n = len(cases)
    det_times, ind_times = [], []
    for case in cases:
        if __check_sat(__get_status(case)) or __check_unsat(__get_status(case)):
            det_times.append(__get_time(case))
        else:
            ind_times.append(tl)

    if len(det_times) == 0:
        return tl

    time_sum = 0.
    for dt in det_times:
        time_sum += dt * n
    for it in ind_times:
        time_sum += it

    new_tl = time_sum / (n * len(det_times) + len(ind_times))
    new_tl = max(1., new_tl)
    best_tl = __choose_best_tl(new_tl, det_times, ind_times)

    for i in range(len(cases)):
        if __check_sat(__get_status(cases[i])) and __get_time(cases[i]) > best_tl:
            cases[i] = __change_status(cases[i])

    return best_tl


def throw_corrector(cases, tl):
    pass


def __check_sat(status):
    for sat_status in sat_statuses:
        if sat_status == status:
            return True
    return False


def __check_unsat(status):
    for unsat_status in unsat_statuses:
        if unsat_status == status:
            return True
    return False


def __get_status(case):
    if isinstance(case, tuple):
        return case[0]
    elif isinstance(case, KeyGenerator):
        return case.status


def __change_status(case):
    if isinstance(case, tuple):
        return dis_statuses[1], case[1]
    elif isinstance(case, KeyGenerator):
        case.status = dis_statuses[0]
        return case


def __get_time(case):
    if isinstance(case, tuple):
        return case[1]
    elif isinstance(case, KeyGenerator):
        return case.time


def __choose_best_tl(min_tl, det_times, ind_times):
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
