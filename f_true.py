from algorithm.a5_1 import A5_1
from algorithm.a5_toy import A5_toy
from algorithm.trivium_64 import Trivium_64
from module.predictive_function import PredictiveFunction
from util import formatter, constant
from wrapper.lingeling import LingelingWrapper
from wrapper.minisat import MinisatWrapper
from wrapper.plingeling import PLingelingWrapper
import numpy as np

solver_wrappers = {
    "minisat": MinisatWrapper(constant.minisat_path),
    "lingeling": LingelingWrapper(constant.lingeling_path),
    "plingeling": PLingelingWrapper(constant.plingeling_path, 4)
}

pf_parameters = {
    "crypto_algorithm": Trivium_64,
    "cnf_link": constant.trivium_64_cnf,
    "threads": 32,
    "N": 100000,
    "solver_wrapper": solver_wrappers["lingeling"],
}

cases = [
    formatter.format_to_array('0000001010111101001000000010101111101100000010000100001000101000(22)')
    # , formatter.format_to_array('0000010110101001010000111011101000110000001000101010010001010000(23)')
    # , formatter.format_to_array('0100100111001011001100010001000101100100000001100010001010001100(23)')
    # , formatter.format_to_array('0100011001011001000000100110001111110100000010010100000100001000(22)')
    # , formatter.format_to_array('0101101010011001000000000011011100010110001100000100001001100000(22)')
]

case = np.zeros(64, dtype=np.int)
numbers = [8, 12, 15, 19, 20, 23, 25, 26, 27, 31, 33, 35, 38, 39, 46, 50, 51, 54, 61, 62]
for i in numbers:
    case[i - 1] = 1

cases.append(case)


# for c in cases:
#     ss = ""
#     for i in range(len(c)):
#         if c[i]:
#             ss += str(i + 1) + ", "
#     ss += ""
#     print ss
# exit(0)

# for c in cases:
#     print formatter.format_array(c)

metrics = []

# ss = "B = { "
# for i in range(len(cases[1])):
#     if cases[1][i]:
#         ss += "a" + str(i + 1) + ", "
# ss += "}"
# print ss
# exit(0)

for case in cases:
    print "start with mask: " + formatter.format_array(case)
    pf = PredictiveFunction(pf_parameters)
    metric, time_stats = pf.compute(case)
    metrics.append(metric)
    print "true metric: " + str(metric)
    print "------------------------------------------------------"

print "------------------------------------------------------"
print "------------------------------------------------------"
for i in range(len(cases)):
    print "metric for mask " + formatter.format_array(cases[i]) + ": " + str(metrics[i])
