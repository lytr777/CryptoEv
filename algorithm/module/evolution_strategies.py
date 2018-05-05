import numpy as np


class PopulationRoulette:
    def __init__(self, alive_count, sorted_P_v):
        self.Q_roulette = []
        s = 0.
        for i in range(alive_count):
            v = 0.
            for j in range(alive_count):
                v += sorted_P_v[i][1] / sorted_P_v[j][1]
            s = s + (1. / v) if (i + 1 < alive_count) else 1.
            self.Q_roulette.append((sorted_P_v[i][0], s))

    def get_individual(self, p):
        for q in self.Q_roulette:
            if q[1] >= p:
                return q[0]


class EvolutionStrategy:
    def __init__(self, alive_count):
        self.alive_count = alive_count

    def get_population_size(self):
        raise NotImplementedError

    def get_next_population(self, mutation_f, sorted_P_v):
        raise NotImplementedError

    def get_roulette(self, sorted_P_v):
        return PopulationRoulette(self.alive_count, sorted_P_v)

    def get_Q(self, sorted_P_v):
        Q = []
        for i in range(self.alive_count):
            Q.append(sorted_P_v[i][0])

        return Q


class MuCommaLambda(EvolutionStrategy):
    def __init__(self, mu, lmbda):
        EvolutionStrategy.__init__(self, mu)
        self.mu = mu
        self.lmbda = lmbda

    def get_population_size(self):
        return self.lmbda

    def get_next_population(self, mc_f, sorted_P_v):
        mutation_f = mc_f[0]
        P = []
        roulette = self.get_roulette(sorted_P_v)
        distribution = np.random.rand(self.lmbda)
        for i in range(self.lmbda):
            q = roulette.get_individual(distribution[i])
            new_p = mutation_f(q)
            P.append(new_p)

        return P

    def __str__(self):
        return "(%d, %d)" % (self.mu, self.lmbda)


class MuPlusLambda(MuCommaLambda):
    def __init__(self, mu, lmbda):
        MuCommaLambda.__init__(self, mu, lmbda)

    def get_population_size(self):
        return self.mu + self.lmbda

    def get_next_population(self, mc_f, sorted_P_v):
        P = MuCommaLambda.get_next_population(self, mc_f, sorted_P_v)
        P.extend(self.get_Q(sorted_P_v))
        return P

    def __str__(self):
        return "(%d + %d)" % (self.mu, self.lmbda)
