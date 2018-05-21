from algorithm import MetaAlgorithm
from util import formatter, generator
import numpy as np
from copy import copy


class EvolutionAlgorithm(MetaAlgorithm):
    name = "Evolution Algorithm"

    def __init__(self, ev_parameters):
        MetaAlgorithm.__init__(self, ev_parameters)
        self.mutation_f = ev_parameters["mutation_function"]
        self.crossover_f = ev_parameters["crossover_function"]
        self.stagnation_limit = ev_parameters["stagnation_limit"]
        self.strategy = ev_parameters["evolution_strategy"]

    def get_iteration_size(self):
        return self.strategy.get_population_size()

    def start(self, mf_parameters):
        algorithm = mf_parameters["crypto_algorithm"][0]
        max_value = 2 ** algorithm.secret_key_len
        it = 1
        mf_calls = 0
        stagnation = 0
        updated_logs = {}

        if "adaptive_N" in mf_parameters:
            adaptive_selection = mf_parameters["adaptive_N"]
            adaptive_selection.choose_function(algorithm.tag)
        else:
            adaptive_selection = None

        P = self.__restart(algorithm)
        best = (np.zeros(algorithm.secret_key_len, dtype=np.int), max_value, [])
        locals_list = []

        self.print_info(algorithm.name, "%s" % self.strategy)

        while not self.stop_condition(it, mf_calls, len(locals_list)):
            self.print_iteration_header(it)
            P_v = []
            for p in P:
                key = formatter.format_array(p)
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

                    mf = self.minimization_function(mf_parameters)
                    result = mf.compute(p)
                    value, mf_log = result[0], result[1]
                    n = mf_parameters["N"]
                    mf_calls += 1
                    self.value_hash[key] = value, n

                    if len(result) > 2:
                        p_v = (p, value, result[2])
                        if self.comparator(best, p_v) < 0 and len(best[2]) < n:
                            ad_key = formatter.format_array(best[0])
                            mf_copy = copy(mf_parameters)
                            mf_copy["N"] = n - len(best[2])

                            mf = self.minimization_function(mf_copy)
                            ad_result = mf.compute(p, best[2])
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
                P = self.__restart(algorithm)
                locals_list.append(best)
                self.print_local_info(best)
                best = (np.zeros(algorithm.secret_key_len, dtype=np.int), max_value)
                stagnation = 0
            else:
                P_v.sort(cmp=self.comparator)
                P = self.strategy.get_next_population((self.mutation_f, self.crossover_f), P_v)
            it += 1

        if best[1] != max_value:
            locals_list.append(best)
            self.print_local_info(best)

        return locals_list

    def __restart(self, algorithm):
        P = []
        for i in range(self.strategy.get_population_size()):
            P.append(generator.generate_mask(algorithm.secret_key_len, self.s))

        return P
