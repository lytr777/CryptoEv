from util.options import minimization_functions
from util import formatter, constant, configurator

import numpy as np

value_hash = {}
_, _, mf_p = configurator.load('configurations/true.json', value_hash)
m_function = minimization_functions["ibs"]

cases = [formatter.format_to_array("1100111110000100000110111001110000100001011100110111000001010101")]

# case = np.zeros(64, dtype=np.int)
# # numbers = [5, 19, 20, 22, 23, 31, 32, 34, 35, 45, 46, 47, 49, 50, 58, 59, 61, 62, 64, 74, 76, 77, 86, 88, 101, 113, 115,
# #            116, 127, 128, 129, 130, 131, 133, 140, 142, 143, 144, 145, 146, 154, 155, 156, 157, 158, 160, 161, 170, 172,
# #            173]
# numbers = [
#     1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 42, 43, 44, 45, 46, 47, 48, 49, 50,
#     51, 52
# ]
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

with open(constant.true_log_path, 'w+'):
    pass

values = []
for case in cases:
    log = "start with mask: %s\n" % formatter.format_array(case)
    mf = m_function(mf_p)
    value, mf_log = mf.compute(case)
    values.append(value)

    log += mf_log
    log += "true value: %.7g\n" % value
    log += "------------------------------------------------------\n"

    with open(constant.true_log_path, 'a') as f:
        f.write(log)

true_log = "------------------------------------------------------\n"
true_log += "------------------------------------------------------\n"
for i in range(len(cases)):
    true_log += "value for mask %s: %.7g\n " % (formatter.format_array(cases[i]), values[i])

with open(constant.true_log_path, 'a') as f:
    f.write(true_log)
