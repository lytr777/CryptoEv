from copy import copy

import numpy as np

from algorithm import MetaAlgorithm
from model.case_generator import CaseGenerator
from parse_utils.cnf_parser import CnfParser
from util import constant


class TabuSearch(MetaAlgorithm):
    name = "Tabu Search"

    def __init__(self, ts_parameters):
        MetaAlgorithm.__init__(self, ts_parameters)
        self.update_count = ts_parameters["update_count"]

    def start(self, mf_parameters):
        algorithm = mf_parameters["key_generator"]
        cnf_path = constant.cnfs[algorithm.tag]
        cnf = CnfParser().parse_for_path(cnf_path)
        rs = np.random.RandomState(43)
        cg = CaseGenerator(algorithm, cnf, rs, self.backdoor)

        it = 1
        it_updates = 0
        mf_calls = 0
        locals_list = []
        tabu_list = {}

        self.print_info(algorithm.name)
        center, value = self.__get_new_center(cg, mf_parameters)
        best = (center, value)

        while not self.stop_condition(it, mf_calls, len(locals_list), best[1]):
            self.print_iteration_header(it)
            updated = False
            for x in self.__get_neighbourhood(center):
                self.backdoor.set(x)
                key = str(self.backdoor)
                if key in self.value_hash:
                    hashed = True
                    value, mf_log = self.value_hash[key], ""
                else:
                    hashed = False
                    mf = self.predictive_function(mf_parameters)
                    result = mf.compute(cg)
                    value, mf_log = result[0], result[1]
                    mf_calls += 1
                    self.value_hash[key] = value

                if key in tabu_list:
                    self.print_tabu_log(key, value)
                else:
                    if self.comparator(best, (x, value)) > 0:
                        best = (x, value)
                        updated = True
                        it_updates += 1

                    self.print_mf_log(hashed, key, value, mf_log)

                if self.update_count <= it_updates:
                    break

            if updated:
                center_key = self.backdoor.to_str(best[0])
                tabu_list[center_key] = best[1]
                center = best[0]
            else:
                locals_list.append((self.backdoor.snapshot(best[0]), best[1]))
                self.print_local_info(best)
                center, value = self.__get_new_center(cg, mf_parameters)
                best = (center, value)

            it += 1
            it_updates = 0

        return locals_list

    def __get_new_center(self, cg, mf_parameters):
        self.backdoor.reset()
        center = self.backdoor.get()
        key = str(self.backdoor)

        if key in self.value_hash:
            value = self.value_hash[key]
        else:
            mf = self.predictive_function(mf_parameters)
            result = mf.compute(cg)
            value = result[0]
            self.value_hash[key] = value

        return center, value

    @staticmethod
    def __get_neighbourhood(vector):
        for i in range(len(vector)):
            new_vector = copy(vector)
            new_vector[i] = not new_vector[i]
            yield new_vector

    def print_tabu_log(self, key, value):
        with open(self.log_file, 'a') as f:
            f.write("------------------------------------------------------\n")
            f.write("mask: %s in tabu list\n" % key)
            f.write("with value: %.7g\n" % value)
