import numpy as np
from copy import copy

from constants.runtime import runtime_constants as rc
from algorithm import MetaAlgorithm, Condition
from model.case_generator import CaseGenerator
from util.parse.cnf_parser import CnfParser
from constants import static


class EvolutionAlgorithm(MetaAlgorithm):
    name = "evolution"

    def __init__(self, **kwargs):
        MetaAlgorithm.__init__(self, **kwargs)
        self.strategy = kwargs["strategy"]
        self.mutation = kwargs["mutation_function"]
        self.crossover = kwargs["crossover_function"]
        self.stagnation_limit = kwargs["stagnation_limit"]

    def start(self, backdoor):
        predictive_f = rc.configuration["predictive_function"]
        key_generator = predictive_f.key_generator
        cnf_path = static.cnfs[key_generator.tag]
        cnf = CnfParser().parse_for_path(cnf_path)
        rs = np.random.RandomState(43)

        cg = CaseGenerator(key_generator, cnf, rs)

        # if self.mutation_f == LevelMutation:
        #     self.mutation_f = LevelMutation(cnf, algorithm)

        condition = Condition()
        condition.set("stagnation", 1)
        max_value = float("inf")
        updated_logs = {}

        P = self.__restart(backdoor)
        best = (backdoor, max_value, [])
        locals_list = []

        while not self.stop_condition.check(condition):
            self.print_iteration_header(condition.get("iteration"))
            P_v = []
            for p in P:
                key = str(p)
                if key in rc.value_hash:
                    hashed = True
                    if key in updated_logs:
                        logs = updated_logs[key]
                        updated_logs.pop(key)
                    else:
                        logs = ""
                    (value, _), pf_log = rc.value_hash[key], logs

                    p_v = (p, value)
                else:
                    hashed = False

                    c_out = predictive_f.compute(cg, p)
                    r = predictive_f.calculate(cg, p, c_out)
                    condition.increase("pf_calls")
                    value, pf_log = r[0], r[1]
                    rc.value_hash[key] = r[0], len(r[2])

                    p_v = (p, r[0], r[2])
                    if self.comparator.compare(best, p_v) < 0 and len(best[2]) < len(p_v[2]):
                        ad_key = str(best[0])
                        ad_c_out = predictive_f.compute(cg, best[0], best[2])
                        ad_r = predictive_f.calculate(cg, best[0], ad_c_out)
                        updated_logs[ad_key] = ad_r[1]

                        best = (best[0], ad_r[0], ad_r[2])
                        rc.value_hash[ad_key] = ad_r[0], len(ad_r[2])

                    if self.comparator.compare(best, p_v) > 0:
                        best = p_v
                        condition.set("stagnation", -1)

                P_v.append(p_v)
                self.print_pf_log(hashed, key, value, pf_log)

            condition.increase("stagnation")
            condition.set("pf_value", best[1])
            if condition.get("stagnation") >= self.stagnation_limit:
                locals_list.append((best[0], best[1]))
                condition.increase("local_count")
                self.print_local_info(best)
                P = self.__restart(backdoor)

                predictive_f.selection.reset()
                best = (backdoor, max_value, [])
                condition.set("stagnation", 0)
            else:
                P_v.sort(cmp=self.comparator.compare)
                P = self.strategy.get_next_population((self.mutation.mutate, self.crossover.cross), P_v)
            condition.increase("iteration")

        if best[1] != max_value:
            locals_list.append((best[0], best[1]))
            condition.increase("local_count")
            self.print_local_info(best)

        return locals_list

    def get_info(self):
        info = MetaAlgorithm.get_info(self)
        info += "-- %s\n" % str(self.strategy)
        info += "-- %s\n" % str(self.mutation)
        info += "-- %s\n" % str(self.crossover)
        info += "-- stagnation limit: %s\n" % str(self.stagnation_limit)
        return info

    def __restart(self, backdoor):
        P = []
        for i in range(self.strategy.get_population_size()):
            P.append(copy(backdoor))

        return P
