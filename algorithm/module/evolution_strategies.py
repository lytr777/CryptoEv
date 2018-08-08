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

    def get_next_population(self, mc_f, sorted_P_v):
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
        return "Strategy (%d, %d)" % (self.mu, self.lmbda)


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
        return "strategy: (%d + %d)" % (self.mu, self.lmbda)


class Genetic(EvolutionStrategy):
    def __init__(self,  m, l, c):
        EvolutionStrategy.__init__(self, m + l + c)
        self.m = m
        self.l = l
        self.c = c

    def get_population_size(self):
        return self.m + self.l + self.c

    def get_next_population(self, mc_f, sorted_P_v):
        mutation_f = mc_f[0]
        crossover_f = mc_f[1]
        P = []
        for i in range(self.l):
            P.append(sorted_P_v[i][0])

        roulette = self.get_roulette(sorted_P_v)
        distribution = np.random.rand(self.m)
        for i in range(self.m):
            q = roulette.get_individual(distribution[i])
            new_p = mutation_f(q)
            P.append(new_p)

        distribution = np.random.rand(self.c * 3)
        for i in range(self.c):
            v = roulette.get_individual(distribution[i])
            w = roulette.get_individual(distribution[self.c + i])

            new_v, new_w = crossover_f(v, w)
            P.append(new_v if distribution[2 * self.c + i] < 0.5 else new_w)

        return P

    def __str__(self):
        return "genetic: (%d, %d, %d)" % (self.m, self.l, self.c)

