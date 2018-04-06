from util import mutation, formatter, generator
import numpy as np


class EvolutionAlgorithm:
    def __init__(self, ev_parameters):
        self.s = ev_parameters["start_s"]
        self.min_s = ev_parameters["min_s"]
        self.comparator = ev_parameters["comparator"]
        self.minimization_function = ev_parameters["minimization_function"]
        self.stop_condition = ev_parameters["stop_condition"]
        self.mutation_strategy = ev_parameters["mutation_strategy"]
        self.value_hash = ev_parameters["value_hash"]
        self.stagnation_limit = ev_parameters["stagnation_limit"]

        self.lmbda = ev_parameters["lambda"] if ("lambda" in ev_parameters) else 1
        self.mu = ev_parameters["mu"] if ("mu" in ev_parameters) else 1

    def start(self, mf_parameters):
        algorithm = mf_parameters["crypto_algorithm"][0]
        max_value = 2 ** algorithm.secret_key_len
        it = 0
        stagnation = 0

        P = self.__restart(algorithm)
        best = (np.zeros(algorithm.secret_key_len, dtype=np.int), max_value)
        best_locals = []

        while not self.stop_condition(it, best[1], len(best_locals)):
            P_v = []
            print "------------------------------------------------------"
            print "iteration step: " + str(it)
            for p in P:
                key = formatter.format_array(p)
                if key in self.value_hash:
                    print "------------------------------------------------------"
                    print "mask: " + key + " has been saved in hash"
                    value = self.value_hash[key]
                    print "with value: " + str("%.7g" % value)
                    p_v = (p, value)
                else:
                    print "------------------------------------------------------"
                    print "start prediction with mask: " + key
                    pf = self.minimization_function(mf_parameters)
                    value, stats = pf.compute(p)
                    for stat in stats:
                        print stat
                    self.value_hash[key] = value
                    print "end prediction with value: " + str("%.7g" % value)
                    p_v = (p, value)

                if self.comparator(best, p_v) > 0:
                    best = p_v
                    stagnation = -1

                P_v.append(p_v)

            stagnation += 1
            if stagnation >= self.stagnation_limit:
                P = self.__restart(algorithm)
                best_locals.append(best)
                best = (np.zeros(algorithm.secret_key_len, dtype=np.int), max_value)
                stagnation = 0
            else:
                Q = self.__get_bests(P_v)
                P = self.__mutation(Q)
            it += 1
        if best[0] != max_value:
            best_locals.append(best)
        return best_locals

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
            for i in range(self.lmbda / self.mu):
                new_p = self.mutation_strategy(q)
                mutation.zero_mutation(new_p, self.min_s)
                P.append(new_p)

        return P
