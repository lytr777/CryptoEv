from copy import copy

import numpy as np

from algorithm import MetaAlgorithm, Condition
from constants import static
from model.case_generator import CaseGenerator
from util.parse.cnf_parser import CnfParser
from constants.runtime import runtime_constants as rc


class TabuSearch(MetaAlgorithm):
    name = "tabu"

    def __init__(self, **kwargs):
        MetaAlgorithm.__init__(self, **kwargs)
        self.update_count = kwargs["update_count"]

    def start(self, backdoor):
        predictive_f = rc.configuration["predictive_function"]
        key_generator = predictive_f.key_generator
        cnf_path = static.cnfs[key_generator.tag]
        cnf = CnfParser().parse_for_path(cnf_path)
        rs = np.random.RandomState()

        cg = CaseGenerator(key_generator, cnf, rs)

        condition = Condition()
        condition.set("it_updates", 0)
        max_value = float("inf")
        updated_logs = {}

        locals_list = []
        tabu_list = {}

        best = (backdoor, max_value, [])
        center = backdoor

        while not self.stop_condition(condition):
            self.print_iteration_header(condition.get("iteration"))
            updates = 0
            for x in self.__get_neighbourhood(center):
                key = str(x)
                if key in rc.value_hash:
                    if key in updated_logs:
                        logs = updated_logs[key]
                        updated_logs.pop(key)
                    else:
                        logs = ""
                    (value, _), pf_log = rc.value_hash[key], logs

                    x_v = (x, value)
                else:
                    hashed = False
                    c_out = predictive_f.compute(cg, p)
                    r = predictive_f.calculate(cg, p, c_out)
                    condition.increase("pf_calls")

                    value, pf_log = r[0], r[1]
                    rc.value_hash[key] = r[0], len(r[2])

                    x_v = (x, r[0], r[2])

                    if key in tabu_list:
                        self.__print_tabu_log(key, value)
                    else:
                        if self.comparator.compare(best, x_v) < 0 and len(best[2]) < len(x_v[2]):
                            ad_key = str(best[0])
                            ad_c_out = predictive_f.compute(cg, best[0], best[2])
                            ad_r = predictive_f.calculate(cg, best[0], ad_c_out)
                            updated_logs[ad_key] = ad_r[1]

                            best = (best[0], ad_r[0], ad_r[2])
                            rc.value_hash[ad_key] = ad_r[0], len(ad_r[2])

                        if self.comparator.compare(best, x_v) > 0:
                            best = x_v
                            updates += 1





                    self.print_pf_log(hashed, key, value, pf_log)

                if self.update_count <= it_updates:
                    break

            if updated:
                center_key = str(best[0])
                tabu_list[center_key] = best[1]
                center = best[0]
            else:
                locals_list.append((best[0], best[1]))
                self.print_local_info(best)
                center, value = self.__get_new_center(cg, pf_parameters)
                best = (self.init_backdoor, value)

            it += 1
            it_updates = 0

        return locals_list

    def __get_new_center(self, cg, pf_parameters):
        key = str(self.init_backdoor)

        if key in self.value_hash:
            value = self.value_hash[key]
        else:
            pf = self.p_function(pf_parameters)
            result = pf.compute(cg, self.init_backdoor)
            value = result[0]
            self.value_hash[key] = value

        return self.init_backdoor, value

    def __get_neighbourhood(self, backdoor):
        v = backdoor.get_mask()
        for i in range(len(v)):
            new_v = copy(v)
            new_v[i] = not new_v[i]
            yield backdoor.get_copy(new_v)

    def get_info(self):
        info = MetaAlgorithm.get_info(self)
        info += "-- update count: %s\n" % str(self.update_count)
        return info

    def __print_tabu_log(self, key, value):
        rc.logger.write("------------------------------------------------------\n",
                        "mask: %s in tabu list\n" % key,
                        "with value: %.7g\n" % value)
