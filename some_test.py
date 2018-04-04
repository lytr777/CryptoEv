import collections

from algorithm.evolution import EvolutionAlgorithm
from module import decomposition
from options import minimization_functions, mutation_strategy, stop_conditions
from options import crypto_algorithms, solver_wrappers, multi_solvers
from util import comparator, corrector

from time import time


class EmptyHash(collections.MutableMapping):
    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass

    def __len__(self):
        return 0

    def __iter__(self):
        pass

    def __getitem__(self, key):
        raise KeyError


empty_hash = EmptyHash()

ev_parameters = {
    "start_s": 120,
    "min_s": 0,
    "comparator": comparator.compare,
    "minimization_function": minimization_functions["ibs"],
    "mutation_strategy": mutation_strategy["normally"],
    "stop_condition": stop_conditions(20, 2 ** 20, 5)["iterative"],
    "value_hash": empty_hash,
    "stagnation_limit": 100,

    "lambda": 1,
    "mu": 1
}

ev_alg = EvolutionAlgorithm(ev_parameters)

mf_parameters = {
    "crypto_algorithm": crypto_algorithms["bivium"],
    "threads": 32,
    "N": 300,
    "solver_wrapper": solver_wrappers["lingeling"],
    "multi_solver": multi_solvers["worker"],
    "time_limit": 1,
    "corrector": corrector.mass_corrector(coefficient=10),
    "decomposition": decomposition.decomposition(empty_hash),
    "d": 5, # 2^d == threads
    # "break_time": 900
}

test1 = time()
best_locals = ev_alg.start(mf_parameters)


test2 = time()
mf_parameters["multi_solver"] = multi_solvers["sleep"]
best_locals = ev_alg.start(mf_parameters)


test3 = time()
ev_parameters["start_s"] = 0
mf_parameters["multi_solver"] = multi_solvers["worker"]
best_locals = ev_alg.start(mf_parameters)


test4 = time()
mf_parameters["multi_solver"] = multi_solvers["sleep"]
best_locals = ev_alg.start(mf_parameters)


end = time()
print "-----------------------------"
print "worker, 120: " + str(test2 - test1)
print "sleep, 120: " + str(test3 - test2)
print "worker, 0: " + str(test4 - test3)
print "sleep, 0: " + str(end - test4)
