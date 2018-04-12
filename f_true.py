from options import minimization_functions
from options import crypto_algorithms, solver_wrappers, multi_solvers

from util import formatter, constant

import numpy as np

m_function = minimization_functions["gad"]

mf_parameters = {
    "crypto_algorithm": crypto_algorithms["bivium"],
    "cnf_link": constant.bivium_cnf,
    "threads": 32,
    "N": 100000,
    "solver_wrapper": solver_wrappers["rokk_py"],
    "multi_solver": multi_solvers["sleep"],
}

cases = [
    formatter.format_to_array('000000000000001000011000000100010100000001011001000000101000010000000100000000000000000000000000001000000000001101001000010110111000001010111110001010100111000001000101001000000(42)')
    # , formatter.format_to_array('011000000000000000000011110000000000010100010000010001011000000011001000000000110000000000001001100000000010000000001011100000000000111001000000101110011000000111010000000000001(41)')
    # , formatter.format_to_array('000000011000000000010011000000001010110000000000001100000001001000000000011000000000000000010010000010010010000000100001000000001001011000010000011011000101100010000001000010100(41)')
    # , formatter.format_to_array('000000000000000000001011000000010011010000000101011000000001110101001001000010000000000000000000000001000000000001000001000011101110001000001100101001000001001010000001000101000(40)')
]

case = np.zeros(177, dtype=np.int)
numbers = [5, 19, 20, 22, 23, 31, 32, 34, 35, 45, 46, 47, 49, 50, 58, 59, 61, 62, 64, 74, 76, 77, 86, 88, 101, 113, 115,
           116, 127, 128, 129, 130, 131, 133, 140, 142, 143, 144, 145, 146, 154, 155, 156, 157, 158, 160, 161, 170, 172,
           173]
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

with open(constant.true_log_path, 'w+'):
    pass

values = []
for case in cases:
    print "start with mask: " + formatter.format_array(case)
    mf = m_function(mf_parameters)
    value, mf_log = mf.compute(case)
    values.append(value)

    mf_log += "true value: %.7g" % value
    mf_log += "------------------------------------------------------\n"

    with open(constant.true_log_path, 'a') as f:
        f.write(mf_log)

true_log = "------------------------------------------------------\n"
true_log += "------------------------------------------------------\n"
for i in range(len(cases)):
    true_log += "value for mask %s:%.7g\n " % (formatter.format_array(cases[i]), values[i])

with open(constant.true_log_path, 'a') as f:
    f.write(true_log)
