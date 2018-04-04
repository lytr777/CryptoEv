def mass_corrector(coefficient):
    def __mass_corrector(cases, tl):
        det_times, ind_times = [], []
        for case in cases:
            if case.status == "UNSATISFIABLE" or case.status == "SATISFIABLE":
                det_times.append(case.time)
            else:
                ind_times.append(tl)

        if len(det_times) == 0:
            return tl

        time_sum = 0.
        for dt in det_times:
            time_sum += dt * coefficient
        for it in ind_times:
            time_sum += it

        new_tl = time_sum / (coefficient * len(det_times) + len(ind_times))
        best_tl = __choose_best_tl(new_tl, det_times, ind_times)

        for case in cases:
            if case.status == "SATISFIABLE" and case.time > best_tl:
                case.status = "DISCARDED"

        return best_tl

    return __mass_corrector


def __choose_best_tl(min_tl, det_times, ind_times):
    exactly, perhaps = [], []
    for time in det_times:
        if time <= min_tl:
            exactly.append(time)
        else:
            perhaps.append(time)

    perhaps.sort()
    n = len(det_times) + len(ind_times)
    best = (min_tl, min_tl * n / len(exactly))

    for i in range(len(perhaps)):
        value = perhaps[i] * n / (len(exactly) + i + 1)
        if value <= best[1]:
            best = (perhaps[i], value)

    return best[0]

