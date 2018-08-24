import numpy as np

from algorithm import MetaAlgorithm
from module.backdoor_mutation import LevelMutation
from model.case_generator import CaseGenerator
from parse_utils.cnf_parser import CnfParser
from util import constant
from copy import copy


class EvolutionAlgorithm(MetaAlgorithm):
    name = "evolution"

    def __init__(self, ev_parameters):
        MetaAlgorithm.__init__(self, ev_parameters)
        self.mutation_f = ev_parameters["mutation_function"]
        self.crossover_f = ev_parameters["crossover_function"]
        self.stagnation_limit = ev_parameters["stagnation_limit"]
        self.strategy = ev_parameters["evolution_strategy"]

    def start(self, pf_parameters):
        algorithm = pf_parameters["key_generator"]
        cnf_path = constant.cnfs[algorithm.tag]
        cnf = CnfParser().parse_for_path(cnf_path)
        rs = np.random.RandomState(43)
        cg = CaseGenerator(algorithm, cnf, rs)

        if self.mutation_f == LevelMutation:
            self.mutation_f = LevelMutation(cnf, algorithm).mutate

        max_value = float("inf")
        it = 1
        pf_calls = 0
        stagnation = 0
        updated_logs = {}

        if "adaptive_N" in pf_parameters:
            adaptive_selection = pf_parameters["adaptive_N"]
            adaptive_selection.choose_function(algorithm.tag)
        else:
            adaptive_selection = None

        P = self.__restart()
        best = (self.init_backdoor, max_value, [])
        locals_list = []

        solver = pf_parameters["solver_wrapper"].info["tag"]
        tl = pf_parameters["time_limit"] if self.p_function.type == "ibs" else None
        self.print_info(algorithm.tag, solver, tl, str(self.strategy))

        while not self.stop_condition(it, pf_calls, len(locals_list), best[1]):
            self.print_iteration_header(it)
            P_v = []
            for p in P:
                key = str(p)
                if key in self.value_hash:
                    hashed = True
                    if key in updated_logs:
                        logs = updated_logs[key]
                        updated_logs.pop(key)
                    else:
                        logs = ""
                    (value, n), pf_log = self.value_hash[key], logs

                    p_v = (p, value)
                else:
                    hashed = False
                    if adaptive_selection is not None:
                        pf_parameters["N"] = adaptive_selection.get_N(best)

                    pf = self.p_function(pf_parameters)
                    result = pf.compute(cg, p)
                    value, pf_log = result[0], result[1]
                    n = pf_parameters["N"]
                    pf_calls += 1
                    self.value_hash[key] = value, n

                    if len(result) > 2:
                        p_v = (p, value, result[2])
                        if self.comparator(best, p_v) < 0 and len(best[2]) < n:
                            ad_key = str(best[0])
                            pf_copy = copy(pf_parameters)
                            pf_copy["N"] = n - len(best[2])

                            pf = self.p_function(pf_copy)
                            ad_result = pf.compute(cg, best[0], best[2])
                            updated_logs[ad_key] = ad_result[1]

                            best = (best[0], ad_result[0], ad_result[2])
                            self.value_hash[ad_key] = ad_result[0], n
                    else:
                        p_v = (p, value)

                    if self.comparator(best, p_v) > 0:
                        best = p_v
                        stagnation = -1

                P_v.append(p_v)
                self.print_pf_log(hashed, key, value, pf_log)

            stagnation += 1
            if stagnation >= self.stagnation_limit:
                locals_list.append((best[0], best[1]))
                self.print_local_info(best)
                P = self.__restart()
                best = (self.init_backdoor, max_value, [])
                stagnation = 0
            else:
                P_v.sort(cmp=self.comparator)
                P = self.strategy.get_next_population((self.mutation_f, self.crossover_f), P_v)
            it += 1

        if best[1] != max_value:
            locals_list.append((best[0], best[1]))
            self.print_local_info(best)

        return locals_list

    def __restart(self):
        P = []
        for i in range(self.strategy.get_population_size()):
            P.append(copy(self.init_backdoor))

        return P
