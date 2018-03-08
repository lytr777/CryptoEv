from key_generators.a5_1 import A5_1
from key_generators.a5_toy import A5_toy
from key_generators.trivium_64 import Trivium_64
from key_generators.bivium import Bivium

from wrapper.lingeling import LingelingWrapper
from wrapper.minisat import MinisatWrapper
from wrapper.plingeling import PLingelingWrapper
from wrapper.rokk import RokkWrapper
from wrapper.rokk_py import RokkPyWrapper

from module.gad_function import GADFunction
from module.ibs_function import IBSFunction
from module import decomposition

from algorithm.evolution import EvolutionAlgorithm

from util import formatter, constant, mutation, parser, ploter

value_hash = {}

solver_wrappers = {
    "minisat": MinisatWrapper(constant.minisat_path),
    "lingeling": LingelingWrapper(constant.lingeling_path),
    "rokk": RokkWrapper(constant.rokk_path),
    "rokk_py": RokkPyWrapper(constant.rokk_py_path),
    "plingeling": PLingelingWrapper(constant.plingeling_path, 4)
}

stop_conditions = {
    "iterative": lambda it, met, res: it > 3000,
    "value": lambda it, met, res: met < 2 ** 20,
    "mix": lambda it, met, res: it > 10000 or met < 2 ** 20,
}

mutation_strategy = {
    "neighbour": mutation.neighbour_mutation,
    "normally": mutation.normally_mutation,
    "scaled": lambda v: mutation.scaled_mutation(2., v),
    "swap": mutation.swap_mutation
}

minimization_functions = {
    "gad": GADFunction,
    "ibs": IBSFunction
}

# Init parameters

ev_parameters = {
    "start_s": 120,
    "min_s": 0,
    "minimization_function": minimization_functions["ibs"],
    "mutation_strategy": mutation_strategy["normally"],
    "stop_condition": stop_conditions["iterative"],
    "value_hash": value_hash,
    "stagnation_limit": 100,

    "lambda": 1,
    "mu": 1
}

ev_alg = EvolutionAlgorithm(ev_parameters)

mf_parameters = {
    "crypto_algorithm": Bivium,
    "cnf_link": constant.bivium_cnf,
    "threads": 32,
    "N": 300,
    "solver_wrapper": solver_wrappers["lingeling"],
    "time_limit": 1,
    "decomposition": lambda m, k, d, p, f: decomposition.decomposition(value_hash, m, k, d, p, f),
    "d": 5,  # 2^d == threads
    # "break_time": 900
}

# parser.restore_hash(value_hash, "./out/21.02.bivium_log", 2)
# parser.restore_hash(value_hash, "./out/8.02.trivium_64_log", 2)
# parser.restore_hash(value_hash, "./out/9.02.trivium_64_log", 2)


# data1 = parser.parse_out("./out/6.03.bivium_rokk_log", 2)
# ploter.show_plot([data1])
#
# exit(0)

best_locals = ev_alg.start(mf_parameters)
best = (None, 2 ** 64)
if len(best_locals) > 0:
    best = best_locals[0]
print "------------------------------------------------------"
print "------------------------------------------------------"
print "------------------------------------------------------"
for best_local in best_locals:
    if best[1] > best_local[1]:
        best = best_local
    print "best local: " + formatter.format_array(best_local[0]) + " with value: " + str("%.7g" % best_local[1])

if best:
    print "------------------------------------------------------"
    print "------------------------------------------------------"
    print "------------------------------------------------------"
    print "best: " + formatter.format_array(best[0]) + " with value: " + str("%.7g" % best[1])
