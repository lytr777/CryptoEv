import sys

from options import minimization_functions, mutation_strategy, stop_conditions
from options import crypto_algorithms, solver_wrappers, multi_solvers
from util import formatter, comparator, corrector, parser, plotter, constant

from module import decomposition
from algorithm.evolution import EvolutionAlgorithm

if len(sys.argv) < 2:
    print "USAGE: main.py <log id>"
    exit(1)

log_file = constant.log_path + sys.argv[1]
value_hash = {}

ev_parameters = {
    "log_file": log_file,
    "start_s": 120,
    "min_s": 0,
    "comparator": comparator.compare,
    "minimization_function": minimization_functions["gad"],
    "mutation_strategy": mutation_strategy["normally"],
    "stop_condition": stop_conditions(2, 2 ** 20, 5)["iterable"],
    "value_hash": value_hash,
    "stagnation_limit": 100,

    "lambda": 1,
    "mu": 1
}

ev_alg = EvolutionAlgorithm(ev_parameters)

# 300, 32 ~ 200 sec
# 300, 8 ~ 230 sec
# 300, 4 ~ 250 sec

mf_parameters = {
    "crypto_algorithm": crypto_algorithms["bivium"],
    "threads": 4,
    "N": 300,
    "solver_wrapper": solver_wrappers["rokk_py"],
    "multi_solver": multi_solvers["worker"],
    "time_limit": 1,
    "corrector": corrector.mass_corrector(coefficient=10),
    "decomposition": decomposition.decomposition(value_hash),
    "d": 2,  # 2^d == threads
    # "break_time": 2
}

# data1 = parser.parse_out("./out/02.04.ibs.rokk.bivium_log", 2)
# plotter.show_plot([data1])
# exit(0)

with open(log_file, 'w+'):
    pass

best_locals = ev_alg.start(mf_parameters)
best = (None, 2 ** 64)
if len(best_locals) > 0:
    best = best_locals[0]

conclusion = "------------------------------------------------------\n"
conclusion += "------------------------------------------------------\n"
conclusion += "------------------------------------------------------\n"
for best_local in best_locals:
    if best[1] > best_local[1]:
        best = best_local
    conclusion += "best local: %s with value: %.7g\n" % (formatter.format_array(best_local[0]), best_local[1])

if best:
    conclusion += "------------------------------------------------------\n"
    conclusion += "------------------------------------------------------\n"
    conclusion += "------------------------------------------------------\n"
    conclusion += "best: %s with value: %.7g\n" % (formatter.format_array(best[0]), best[1])

with open(log_file, 'a') as f:
    f.write(conclusion)
