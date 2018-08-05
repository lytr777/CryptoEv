import argparse
import numpy as np

from configuration import configurator
from model.case_generator import CaseGenerator
from model.variable_set import Backdoor
from parse_utils.cnf_parser import CnfParser
from util import formatter, constant
from util.debugger import Debugger

parser = argparse.ArgumentParser(description='CryptoEv')
parser.add_argument('id', type=str, help='suffix for log file')
parser.add_argument('backdoor', help='load backdoor from specified file')
parser.add_argument('-cp', metavar='tag/path', type=str, default="true", help='tag or path to configuration file')
parser.add_argument('-v', metavar='0', type=int, default=0, help='[0-3] verbosity level')
parser.add_argument('-d', metavar='path', type=str, help='path to debug file')

args = parser.parse_args()
_, meta_p, mf_p = configurator.load('true', {})
m_function = meta_p["predictive_function"]

true_log_file = constant.true_log_path + args.id

mf_p["debugger"] = Debugger(args.d, args.v)
if args.d is not None:
    open(args.d, 'w+').close()

algorithm = mf_p["key_generator"]
cnf_path = constant.cnfs[algorithm.tag]
cnf = CnfParser().parse_for_path(cnf_path)
cg = CaseGenerator(algorithm, cnf)

backdoor = Backdoor.load(args.backdoor, algorithm)
cg.set_backdoor(backdoor)

mf_p["solver_wrapper"].check_installation()
with open(true_log_file, 'w+') as f:
    f.write("-- Key Generator: %s\n" % algorithm(''))
    f.write("-- N = %d\n" % mf_p["N"])
    f.write("------------------------------------------------------\n")
    f.write("start with backdoor: %s\n" % backdoor)

mf = m_function(mf_p)
result = mf.compute(cg)
value, mf_log = result[0], result[1]

with open(true_log_file, 'a') as f:
    f.write(mf_log + "true value: %.7g\n" % value)
