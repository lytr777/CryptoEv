from copy import copy

import numpy as np

from algorithm import MetaAlgorithm
from model.case_generator import CaseGenerator
from parse_utils.cnf_parser import CnfParser
from util import constant


class TabuSearch(MetaAlgorithm):
    name = "tabu"

    def __init__(self, ts_parameters):
        MetaAlgorithm.__init__(self, ts_parameters)
        self.update_count = ts_parameters["update_count"]

    def start(self, pf_parameters):
        algorithm = pf_parameters["key_generator"]
        cnf_path = constant.cnfs[algorithm.tag]
        cnf = CnfParser().parse_for_path(cnf_path)
        rs = np.random.RandomState(43)
        cg = CaseGenerator(algorithm, cnf, rs)

        it = 1
        it_updates = 0
        pf_calls = 0
        locals_list = []
        tabu_list = {}

        solver = pf_parameters["solver_wrapper"].info["tag"]
        tl = pf_parameters["time_limit"] if self.p_function.type == "ibs" else None
        self.print_info(algorithm.tag, solver, tl)
        center, value = self.__get_new_center(cg, pf_parameters)
        best = (self.init_backdoor, value)

        while not self.stop_condition(it, pf_calls, len(locals_list), best[1]):
            self.print_iteration_header(it)
            updated = False
            for x in self.__get_neighbourhood(center):
                key = str(x)
                if key in self.value_hash:
                    hashed = True
                    value, pf_log = self.value_hash[key], ""
                else:
                    hashed = False
                    pf = self.p_function(pf_parameters)
                    result = pf.compute(cg, x)
                    value, pf_log = result[0], result[1]
                    pf_calls += 1
                    self.value_hash[key] = value

                if key in tabu_list:
                    self.print_tabu_log(key, value)
                else:
                    if self.comparator(best, (x, value)) > 0:
                        best = (x, value)
                        updated = True
                        it_updates += 1

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

    @staticmethod
    def __get_neighbourhood(backdoor):
        v = backdoor.get_mask()
        for i in range(len(v)):
            new_v = copy(v)
            new_v[i] = not new_v[i]
            yield backdoor.get_copy(new_v)

    def print_tabu_log(self, key, value):
        with open(self.log_file, 'a') as f:
            f.write("------------------------------------------------------\n")
            f.write("mask: %s in tabu list\n" % key)
            f.write("with value: %.7g\n" % value)
