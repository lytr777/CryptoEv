def mass_corrector(cases, tl, coef):
    det_times, ind_times = [], []
    for case in cases:
        if case.status == "UNSATISFIABLE" or case.status == "SATISFIABLE":
            det_times.append(case.time)
        else:
            ind_times.append(tl)

    if len(det_times) == 0:
        return tl

    max_sat_time = max(det_times)
    time_sum = 0.
    for dt in det_times:
        time_sum += dt * coef
    for it in ind_times:
        time_sum += it

    new_tl = time_sum / (coef * len(det_times) + len(ind_times))

    return max(new_tl, max_sat_time)
    # return new_tl
