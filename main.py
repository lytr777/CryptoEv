import sys

from options import minimization_functions, mutation_strategy, stop_conditions
from options import crypto_algorithms, solver_wrappers, multi_solvers
from util import formatter, comparator, corrector, parser, plotter, constant, conclusion

from module import decomposition
from algorithm.evolution import EvolutionAlgorithm

if len(sys.argv) < 2:
    print "USAGE: main.py <log id>"
    exit(1)

log_file = constant.log_path + sys.argv[1]
locals_log_file = constant.locals_log_path + sys.argv[1]
value_hash = {}

ev_parameters = {
    "log_file": log_file,
    "locals_log_file": locals_log_file,
    "start_s": 120,
    "min_s": 0,
    "comparator": comparator.compare,
    "minimization_function": minimization_functions["ibs"],
    "mutation_strategy": mutation_strategy["normally"],
    "stop_condition": stop_conditions(2, 2 ** 20, 1)["locals"],
    "value_hash": value_hash,
    "stagnation_limit": 100,

    "lambda": 1,
    "mu": 1
}

ev_alg = EvolutionAlgorithm(ev_parameters)

# 300, 32 ~ 200 sec
# 300,  8 ~ 230 sec
# 300,  4 ~ 250 sec

mf_parameters = {
    "crypto_algorithm": crypto_algorithms["e0"],
    "threads": 4,
    "N": 500,
    "solver_wrapper": solver_wrappers["rokk_py"],
    "multi_solver": multi_solvers["worker"],
    "time_limit": 3,
    "corrector": corrector.mass_corrector(coefficient=12),
    "decomposition": decomposition.decomposition(value_hash),
    "d": 2,  # 2^d == threads
    # "break_time": 2
}

# data1 = parser.parse_out("./out/02.04.ibs.rokk.bivium_log", 2)
# plotter.show_plot([data1])
# exit(0)

with open(log_file, 'w+'):
    pass


locals_list = ev_alg.start(mf_parameters)

conclusion.add_conclusion(log_file, ev_parameters["lambda"] + ev_parameters["mu"], locals_list=locals_list)
