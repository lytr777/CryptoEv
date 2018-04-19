from util import mutation, formatter, generator
import numpy as np


class EvolutionAlgorithm:
    def __init__(self, ev_parameters):
        self.log_file = ev_parameters["log_file"]
        self.locals_log_file = ev_parameters["locals_log_file"]
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
        it = 1
        stagnation = 0

        P = self.__restart(algorithm)
        best = (np.zeros(algorithm.secret_key_len, dtype=np.int), max_value)
        locals_list = []

        while not self.stop_condition(it, best[1], len(locals_list)):
            step_log = "------------------------------------------------------\n"
            step_log += "iteration step: %d\n" % it
            P_v = []
            for p in P:
                key = formatter.format_array(p)
                if key in self.value_hash:
                    hashed = True
                    value = self.value_hash[key]
                    mf_log = ''
                else:
                    hashed = False
                    pf = self.minimization_function(mf_parameters)
                    value, mf_log = pf.compute(p)
                    self.value_hash[key] = value

                p_v = (p, value)
                if self.comparator(best, p_v) > 0:
                    best = p_v
                    stagnation = -1

                P_v.append(p_v)

                step_log += self.__prepare_step_log(hashed, key, value, mf_log)

            with open(self.log_file, 'a') as f:
                f.write(step_log)

            stagnation += 1
            if stagnation >= self.stagnation_limit:
                P = self.__restart(algorithm)
                locals_list.append(best)
                self.__print_local_info(best)
                best = (np.zeros(algorithm.secret_key_len, dtype=np.int), max_value)
                stagnation = 0
            else:
                Q = self.__get_bests(P_v)
                P = self.__mutation(Q)
            it += 1

        if best[1] != max_value:
            locals_list.append(best)
            self.__print_local_info(best)

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
            for i in range(self.lmbda / self.mu):
                new_p = self.mutation_strategy(q)
                mutation.zero_mutation(new_p, self.min_s)
                P.append(new_p)

        return P

    def __print_local_info(self, local):
        with open(self.locals_log_file, 'a') as f:
            f.write("------------------------------------------------------\n")
            f.write("local with mask: %s\n" % formatter.format_array(local[0]))
            f.write("and value: %.7g\n" % local[1])

    @staticmethod
    def __prepare_step_log(hashed, key, value, mf_log):
        s = "------------------------------------------------------\n"
        if hashed:
            s += "mask: %s has been saved in hash\n" % key
            s += "with value: %.7g\n" % value
        else:
            s += "start prediction with mask: %s\n" % key
            s += mf_log
            s += "end prediction with value: %.7g\n" % value

        return s
