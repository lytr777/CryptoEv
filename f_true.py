from algorithm.a5_1 import A5_1
from algorithm.a5_toy import A5_toy
from algorithm.trivium_64 import Trivium_64
from algorithm.bivium import Bivium
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
    "crypto_algorithm": Bivium,
    "cnf_link": constant.bivium_cnf,
    "threads": 32,
    "N": 30000,
    "solver_wrapper": solver_wrappers["lingeling"],
}


cases = [
      formatter.format_to_array('000001101000000000000110000001000101001010000000010001000000101110100000000000000000000000000000000000001110100000001010000000101101101100001010001000100000001100100000000000000(37)')
    , formatter.format_to_array('011000000000000000000011110000000000010100010000010001011000000011001000000000110000000000001001100000000010000000001011100000000000111001000000101110011000000111010000000000001(41)')
    , formatter.format_to_array('000000011000000000010011000000001010110000000000001100000001001000000000011000000000000000010010000010010010000000100001000000001001011000010000011011000101100010000001000010100(41)')
    , formatter.format_to_array('000000000000000000001011000000010011010000000101011000000001110101001001000010000000000000000000000001000000000001000001000011101110001000001100101001000001001010000001000101000(40)')
    , formatter.format_to_array('000000110000000000110001000000011110000000001010011000000111110000000001100000000010010000000000000000101000000001100110000000001100001000001100000000010000011000000010100000010(39)')
    , formatter.format_to_array('000000000000000000000010011000000001110011010000100100000000000110101000000101000000000000001010001000000100010000000010000100000001101010010000011100100101100000100000001000101(40)')
    , formatter.format_to_array('000000000001010010000001001100100000001100000000000110101010010010100000000000011101100000000000001000000010101000000000010011001000010000100010000010000100000001110100100000000(40)')
]


# case = np.zeros(64, dtype=np.int)
# numbers = [8, 12, 15, 19, 20, 23, 25, 26, 27, 31, 33, 35, 38, 39, 46, 50, 51, 54, 61, 62]
# for i in numbers:
#     case[i - 1] = 1
#
# cases.append(case)


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
