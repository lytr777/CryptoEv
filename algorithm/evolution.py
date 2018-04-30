from algorithm import MetaAlgorithm
from util import mutation, formatter, generator
import numpy as np


class EvolutionAlgorithm(MetaAlgorithm):
    name = "Evolution Algorithm"

    def __init__(self, ev_parameters):
        MetaAlgorithm.__init__(self, ev_parameters)
        self.mutation_strategy = ev_parameters["mutation_strategy"]
        self.stagnation_limit = ev_parameters["stagnation_limit"]

        self.lmbda = ev_parameters["lambda"] if ("lambda" in ev_parameters) else 1
        self.mu = ev_parameters["mu"] if ("mu" in ev_parameters) else 1

    def get_iteration_size(self):
        return self.lmbda + self.mu

    def start(self, mf_parameters):
        algorithm = mf_parameters["crypto_algorithm"][0]
        max_value = 2 ** algorithm.secret_key_len
        it = 1
        stagnation = 0

        P = self.__restart(algorithm)
        best = (np.zeros(algorithm.secret_key_len, dtype=np.int), max_value)
        locals_list = []

        self.print_info(algorithm.name, "Evolution Strategy (%d + %d)" % (self.lmbda, self.mu))

        while not self.stop_condition(it, best[1], len(locals_list)):
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
                Q = self.__get_bests(P_v)
                P = self.__mutation(Q)
            it += 1

        if best[1] != max_value:
            locals_list.append(best)
            self.print_local_info(best)

        return locals_list

    def __restart(self, algorithm):
        P = []
        for i in range(self.lmbda + self.mu):
            P.append(generator.generate_mask(algorithm.secret_key_len, self.s))

        return P

    def __get_bests(self, P_v):
        P_v.sort(cmp=self.comparator)

        Q = []
        for i in range(min(self.mu, len(P_v))):
            Q.append(P_v[i][0])
        return Q

    def __mutation(self, Q):
        P = []
        for q in Q:
            P.append(q)
            for i in range(self.lmbda / self.mu):  # bad
                new_p = self.mutation_strategy(q)
                mutation.zero_mutation(new_p, self.min_s)
                P.append(new_p)

        return P
