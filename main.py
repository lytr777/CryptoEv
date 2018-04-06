from options import minimization_functions, mutation_strategy, stop_conditions
from options import crypto_algorithms, solver_wrappers, multi_solvers
from util import formatter, comparator, corrector, parser, plotter

from module import decomposition
from algorithm.evolution import EvolutionAlgorithm

value_hash = {}

ev_parameters = {
    "start_s": 120,
    "min_s": 0,
    "comparator": comparator.compare,
    "minimization_function": minimization_functions["ibs"],
    "mutation_strategy": mutation_strategy["normally"],
    "stop_condition": stop_conditions(4000, 2 ** 20, 5)["locals"],
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
    "solver_wrapper": solver_wrappers["lingeling"],
    "multi_solver": multi_solvers["worker"],
    "time_limit": 5,
    "corrector": corrector.mass_corrector(coefficient=10),
    "decomposition": decomposition.decomposition(value_hash),
    "d": 5,  # 2^d == threads
    # "break_time": 900
}

# parser.restore_hash(value_hash, "./out/21.02.bivium_log", 2)
# parser.restore_hash(value_hash, "./out/8.02.trivium_64_log", 2)
# parser.restore_hash(value_hash, "./out/9.02.trivium_64_log", 2)


# data1 = parser.parse_out("./out/02.04.ibs.rokk.bivium_log", 2)
# plotter.show_plot([data1])
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
