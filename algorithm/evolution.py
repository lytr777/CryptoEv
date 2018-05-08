from algorithm import MetaAlgorithm
from util import formatter, generator
import numpy as np


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

        P = self.__restart(algorithm)
        best = (np.zeros(algorithm.secret_key_len, dtype=np.int), max_value)
        locals_list = []

        self.print_info(algorithm.name, "Strategy %s" % self.strategy)

        while not self.stop_condition(it, mf_calls, len(locals_list)):
            self.print_iteration_header(it)
            P_v = []
            for p in P:
                key = formatter.format_array(p)
                if key in self.value_hash:
                    hashed = True
                    value, mf_log = self.value_hash[key], ""
                else:
                    hashed = False
                    mf = self.minimization_function(mf_parameters)
                    value, mf_log = mf.compute(p)
                    mf_calls += 1
                    self.value_hash[key] = value

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
