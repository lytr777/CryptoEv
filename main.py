from key_generators.a5_1 import A5_1
from key_generators.e0 import E0
from key_generators.trivium_64 import Trivium_64
from key_generators.bivium import Bivium

from wrapper.lingeling import LingelingWrapper
from wrapper.minisat import MinisatWrapper
from wrapper.plingeling import PLingelingWrapper
from wrapper.rokk import RokkWrapper
from wrapper.rokk_py import RokkPyWrapper

from solvers.sleep_solver import SleepSolver
from solvers.worker_solver import WorkerSolver
from module.gad_function import GADFunction
from module.ibs_function import IBSFunction
from module import decomposition

from algorithm.evolution import EvolutionAlgorithm

from util import formatter, constant, mutation, comparator, corrector, parser, ploter

value_hash = {}

solver_wrappers = {
    "minisat": MinisatWrapper(constant.minisat_path),
    "lingeling": LingelingWrapper(constant.lingeling_path),
    "rokk": RokkWrapper(constant.rokk_path),
    "rokk_py": RokkPyWrapper(constant.rokk_py_path),
    "plingeling": PLingelingWrapper(constant.plingeling_path, 4)
}

crypto_algorithms = {
    "a5_1" : (A5_1, constant.a5_1_cnf),
    "bivium": (Bivium, constant.bivium_cnf),
    "trivium_64": (Trivium_64, constant.trivium_64_cnf),
    "e0": (E0, constant.e0_cnf)
}

stop_conditions = {
    "iterative": lambda it, met, res: it > 1500,
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

multi_solvers = {
    "sleep": SleepSolver,
    "worker": WorkerSolver
}

# Init parameters

ev_parameters = {
    "start_s": 120,
    "min_s": 0,
    "comparator": comparator.compare,
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
    "crypto_algorithm": crypto_algorithms["e0"],
    "threads": 32,
    "N": 300,
    "solver_wrapper": solver_wrappers["rokk_py"],
    "multi_solver": multi_solvers["worker"],
    "time_limit": 1,
    "corrector": lambda s, t: corrector.mass_corrector(s, t, coef=10),
    "decomposition": lambda m, k, d, p, f: decomposition.decomposition(value_hash, m, k, d, p, f),
    "d": 5, # 2^d == threads
    # "break_time": 900
}

# parser.restore_hash(value_hash, "./out/21.02.bivium_log", 2)
# parser.restore_hash(value_hash, "./out/8.02.trivium_64_log", 2)
# parser.restore_hash(value_hash, "./out/9.02.trivium_64_log", 2)


# data1 = parser.parse_out("./out/02.04.ibs.rokk.bivium_log", 2)
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
