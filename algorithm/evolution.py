from module.predictive_function import PredictiveFunction
from util import mutation, formatter, generator


class EvolutionAlgorithm:
    def __init__(self, ev_parameters):
        self.s = ev_parameters["start_s"]
        self.min_s = ev_parameters["min_s"]
        self.stop_condition = ev_parameters["stop_condition"]
        self.mutation_strategy = ev_parameters["mutation_strategy"]
        self.metric_hash = ev_parameters["metric_hash"]
        self.stagnation_limit = ev_parameters["stagnation_limit"]

        self.lmbda = ev_parameters["lambda"] if ("lambda" in ev_parameters) else 1
        self.mu = ev_parameters["mu"] if ("mu" in ev_parameters) else 1

    def start(self, pf_parameters):
        algorithm = pf_parameters["crypto_algorithm"]
        P = self.__restart(algorithm)
        best = (None, 2 ** algorithm.secret_key_len)
        best_locals = []
        it = 0
        stagnation = 0

        while not self.stop_condition(it, best[1], len(best_locals)):
            metrics = []
            print "------------------------------------------------------"
            print "iteration step: " + str(it)
            for p in P:
                key = formatter.format_array(p)
                if key in self.metric_hash:
                    print "------------------------------------------------------"
                    print "mask: " + key + " has been saved in hash"
                    metric = self.metric_hash[key]
                    print "with metric: " + str(metric)
                else:
                    print "------------------------------------------------------"
                    print "start prediction with mask: " + key
                    pf = PredictiveFunction(pf_parameters)
                    metric, time_stats = pf.compute(p)
                    print time_stats
                    self.metric_hash[key] = metric
                    print "end prediction with metric: " + str(metric)

                if best[1] is None or metric < best[1]:
                    best = (p, metric)
                    stagnation = -1

                metrics.append(metric)

            stagnation += 1
            if stagnation >= self.stagnation_limit:
                P = self.__restart(algorithm)
                best_locals.append(best)
                best = (None, 2 ** algorithm.secret_key_len)
            else:
                Q = self.__get_bests(P, metrics)
                P = self.__mutation(Q)
            it += 1

        best_locals.append(best)

        return best_locals

    def __restart(self, algorithm):
        P = []
        for i in range(self.lmbda + self.mu):
            P.append(generator.generate_mask(algorithm.secret_key_len, self.s))

        return P

    def __get_bests(self, P, m):
        m_P = []
        for i in range(len(P)):
            m_P.append((m[i] + i, P[i]))

        m_P.sort(key=lambda tup: tup[0])
        Q = []
        for i in range(min(self.mu, len(m_P))):
            Q.append(m_P[i][1])
        return Q

    def __mutation(self, Q):
        P = []
        for q in Q:
            for i in range(self.lmbda / self.mu):
                new_p = self.mutation_strategy(q)
                mutation.zero_mutation(new_p, self.min_s)
                P.append(new_p)
            P.append(q)

        return P
