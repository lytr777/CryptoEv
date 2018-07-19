from scipy.stats import mstats
from util import formatter

import numpy as np


class IBSSimulation:
    def __init__(self, parameters):
        self.corrector = parameters["corrector"]
        self.comparator = parameters["comparator"]

        self.max_value = parameters["max_value"]
        self.quantiles_prob = parameters["q_prob"]

    def get_best_case(self, value_hash, cases, tl):
        best, best_i = None, None
        i = 0
        for case in cases:
            current = (case.mask, self.get_value(value_hash, case.mask, case.times, tl))
            if best is None or self.comparator(best, current) > 0:
                best = current
                best_i = i
            i += 1

        return best, best_i

    def compute_value(self, mask, times, tl):
        new_tl, dis_count = self.corrector(times, tl)

        det_count = -dis_count
        for status, time in times:
            if status == "UNSAT" or status == "SAT":
                det_count += 1

        assert det_count >= 0
        xi = det_count / float(len(times))

        if xi != 0:
            return (2 ** np.count_nonzero(mask)) * new_tl * (3 / xi)
        else:
            return self.max_value

    def get_value(self, value_hash, mask, times, tl):
        key = formatter.format_array(mask)
        if len(times) == 0:
            return value_hash[key]
        else:
            value = self.compute_value(mask, times, tl)
            value_hash[key] = value
            return value

    def get_subset(self, times, k):
        n = len(times)
        choice = np.random.choice(n, k, replace=False)
        new_times = []
        for i in choice:
            new_times.append(times[i])

        return new_times

    def edit_subset(self, subset, k):
        subset.reset_filter()
        n = len(subset)
        choice = np.random.choice(n, k, replace=False)
        subset.set_filter(choice)

    def dispersion_values(self, values_hash, mask, times, tl, k, rep, min_value):
        key = formatter.format_array(mask)
        if len(times) > 0:
            values = []
            for j in range(rep):
                subset = self.get_subset(times, k)
                value = self.compute_value(mask, subset, tl)

                values.append(max(value, min_value))

            values_hash[key] = values
        else:
            values = values_hash[key]

        quantiles = mstats.mquantiles(values, prob=self.quantiles_prob, axis=0)
        return values, quantiles

    def dispersion(self, iterations, chunk, parameters):
        ks = parameters["ks"]
        tl = parameters["tl"]
        rep = parameters["rep"]

        main_line = []
        value_hash = {}

        for i in range(len(iterations)):
            best, _ = self.get_best_case(value_hash, iterations[i], tl)
            main_line.append(best[1])

        min_value = 0.7 * main_line[len(main_line) - 1]

        changed = False
        for k in ks:
            if k in chunk:
                continue

            print "start dispersion for k = %d" % k
            changed = True
            values_hash = {}

            points = []
            lines = []
            for i in range(len(iterations)):
                _, best_i = self.get_best_case(value_hash, iterations[i], tl)
                mask, times = iterations[i][best_i].mt()
                values, quantiles = self.dispersion_values(values_hash, mask, times, tl, k, rep, min_value)
                points.append(values)

                while len(lines) < len(quantiles):
                    lines.append([])

                for j in range(len(quantiles)):
                    lines[j].append(quantiles[j])
                print i

            lines.append(main_line)
            chunk.set(k, (points, lines))

        return changed
