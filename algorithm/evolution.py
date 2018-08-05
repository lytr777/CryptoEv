from algorithm import MetaAlgorithm
from model.backdoor_list import BackdoorList
from model.case_generator import CaseGenerator
from model.variable_set import Backdoor
from parse_utils.cnf_parser import CnfParser
from util import constant
from copy import copy


class EvolutionAlgorithm(MetaAlgorithm):
    name = "Evolution Algorithm"

    def __init__(self, ev_parameters):
        MetaAlgorithm.__init__(self, ev_parameters)
        self.mutation_f = ev_parameters["mutation_function"]
        self.crossover_f = ev_parameters["crossover_function"]
        self.stagnation_limit = ev_parameters["stagnation_limit"]
        self.strategy = ev_parameters["evolution_strategy"]

    def start(self, mf_parameters):
        algorithm = mf_parameters["key_generator"]
        cnf_path = constant.cnfs[algorithm.tag]
        cnf = CnfParser().parse_for_path(cnf_path)
        cg = CaseGenerator(algorithm, cnf)

        backdoor = Backdoor(algorithm, self.init_backdoor.vars)
        cg.set_backdoor(backdoor)
        max_value = float("inf")
        it = 1
        mf_calls = 0
        stagnation = 0
        updated_logs = {}

        if "adaptive_N" in mf_parameters:
            adaptive_selection = mf_parameters["adaptive_N"]
            adaptive_selection.choose_function(algorithm.tag)
        else:
            adaptive_selection = None

        P = self.__restart()
        best = (BackdoorList(), max_value, [])
        locals_list = []

        self.print_info(algorithm.name, "%s" % self.strategy)

        while not self.stop_condition(it, mf_calls, len(locals_list), best[1]):
            self.print_iteration_header(it)
            P_v = []
            for p in P:
                backdoor.from_list(p)
                key = p.get_key()
                if key in self.value_hash:
                    hashed = True
                    if key in updated_logs:
                        logs = updated_logs[key]
                        updated_logs.pop(key)
                    else:
                        logs = ""
                    (value, n), mf_log = self.value_hash[key], logs

                    p_v = (p, value)
                else:
                    hashed = False
                    if adaptive_selection is not None:
                        mf_parameters["N"] = adaptive_selection.get_N(best)

                    mf = self.predictive_function(mf_parameters)
                    result = mf.compute(cg)
                    value, mf_log = result[0], result[1]
                    n = mf_parameters["N"]
                    mf_calls += 1
                    self.value_hash[key] = value, n

                    if len(result) > 2:
                        p_v = (p, value, result[2])
                        if self.comparator(best, p_v) < 0 and len(best[2]) < n:
                            ad_key = best[0].get_key()
                            mf_copy = copy(mf_parameters)
                            mf_copy["N"] = n - len(best[2])

                            mf = self.predictive_function(mf_copy)
                            ad_result = mf.compute(best[0], best[2])
                            updated_logs[ad_key] = ad_result[1]

                            best = (best[0], ad_result[0], ad_result[2])
                            self.value_hash[ad_key] = ad_result[0], n
                    else:
                        p_v = (p, value)

                    if self.comparator(best, p_v) > 0:
                        best = p_v
                        stagnation = -1

                P_v.append(p_v)
                self.print_mf_log(hashed, key, value, mf_log)

            stagnation += 1
            if stagnation >= self.stagnation_limit:
                P = self.__restart()
                locals_list.append(best)
                self.print_local_info(best)
                best = (BackdoorList(), max_value, [])
                stagnation = 0
            else:
                P_v.sort(cmp=self.comparator)
                P = self.strategy.get_next_population((self.mutation_f, self.crossover_f), P_v)
            it += 1

        if best[1] != max_value:
            locals_list.append(best)
            self.print_local_info(best)

        return locals_list

    def __restart(self):
        P = []
        for i in range(self.strategy.get_population_size()):
            P.append(self.init_backdoor.to_list())

        return P
