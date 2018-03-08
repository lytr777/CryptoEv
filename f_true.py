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

from util import formatter, constant

import numpy as np

solver_wrappers = {
    "minisat": MinisatWrapper(constant.minisat_path),
    "lingeling": LingelingWrapper(constant.lingeling_path),
    "rokk": RokkWrapper(constant.rokk_path),
    "rokk_py": RokkPyWrapper(constant.rokk_py_path),
    "plingeling": PLingelingWrapper(constant.plingeling_path, 4)
}

mf_parameters = {
    "crypto_algorithm": Bivium,
    "cnf_link": constant.bivium_cnf,
    "threads": 32,
    "N": 100000,
    "solver_wrapper": solver_wrappers["rokk_py"],
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

values = []

m_function = GADFunction

for case in cases:
    print "start with mask: " + formatter.format_array(case)
    mf = m_function(mf_parameters)
    value, stats = mf.compute(case)
    values.append(value)
    for stat in stats:
        print stat
    print "true value: " + str("%.7g" % value)
    print "------------------------------------------------------"

print "------------------------------------------------------"
print "------------------------------------------------------"
for i in range(len(cases)):
    print "value for mask " + formatter.format_array(cases[i]) + ": " + str("%.7g" % values[i])
