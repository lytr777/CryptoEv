import numpy

from algorithm.a5_1 import A5_1
from algorithm.a5_toy import A5_toy
from algorithm.trivium_64 import Trivium_64
from algorithm.evolution import EvolutionAlgorithm
from module import decomposition
from module.case_solver import CaseSolver
from util import formatter, constant, mutation, generator, caser, parser, ploter
from util.parser import parse_cnf
from wrapper.lingeling import LingelingWrapper
from wrapper.minisat import MinisatWrapper
from wrapper.plingeling import PLingelingWrapper

metric_hash = {}

solver_wrappers = {
    "minisat": MinisatWrapper(constant.minisat_path),
    "lingeling": LingelingWrapper(constant.lingeling_path),
    "plingeling": PLingelingWrapper(constant.plingeling_path, 4)
}

stop_conditions = {
    "iterative": lambda it, met, res: it > 1500,  # or met < 2 ** 20,
}

mutation_strategy = {
    "neighbour": mutation.neighbour_mutation,
    "normally": mutation.normally_mutation,
    "swap": mutation.swap_mutation
}

# Init parameters

ev_parameters = {
    "start_s": 60,
    "min_s": 0,
    "mutation_strategy": mutation_strategy["normally"],
    "stop_condition": stop_conditions["iterative"],
    "metric_hash": metric_hash,
    "stagnation_limit": 100,

    "lambda": 1,
    "mu": 1
}

ev_alg = EvolutionAlgorithm(ev_parameters)

pf_parameters = {
    "crypto_algorithm": Trivium_64,
    "cnf_link": constant.trivium_64_cnf,
    "threads": 32,
    "N": 300,
    "solver_wrapper": solver_wrappers["lingeling"],
    "decomposition": lambda m, k, d, p: decomposition.decomposition(metric_hash, m, k, d, p),
    "d": 5,  # 2^d == threads
    "break_time": 900
}

parser.restore_hash(metric_hash, "./out/6.02.trivium_64_log", 2)
parser.restore_hash(metric_hash, "./out/8.02.trivium_64_log", 2)

# data1 = parser.parse_out("./out/8.02.trivium_64_log", 2)
# # data2 = parser.parse_out("./out/log_swap_23", 2)
# ploter.show_plot([data1])
#
# exit(0)

best_locals = ev_alg.start(pf_parameters)
best = (None, 2 ** 64)
if len(best_locals) > 0:
    best = best_locals[0]
print "------------------------------------------------------"
print "------------------------------------------------------"
print "------------------------------------------------------"
for best_local in best_locals:
    if best[1] > best_local[1]:
        best = best_local
    print "best local: " + formatter.format_array(best_local[0]) + " with metric: " + str(best_local[1])

if best:
    print "------------------------------------------------------"
    print "------------------------------------------------------"
    print "------------------------------------------------------"
    print "best: " + formatter.format_array(best[0]) + " with metric: " + str(best[1])

# key = generator.generate_key(48)
#
# init_case = caser.create_case(parse_cnf(constant.a5_toy_cnf), {
#     "secret_key": key
# }, A5_toy)
#
# solver = CaseSolver(solver_wrappers["lingeling"])
# solver.start({}, init_case)
# solution_key_stream = init_case.get_solution_key_stream()
#
# simply_case = caser.create_case(parse_cnf(constant.a5_toy_cnf), {
#     "key_stream": solution_key_stream
# }, A5_toy)
#
# simply_case.write_to("./cnf/simply_case")
