import argparse
import numpy as np

from configuration import configurator
from model.case_generator import CaseGenerator
from model.backdoor import InextensibleBackdoor
from parse_utils.cnf_parser import CnfParser
from util import constant
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

backdoor = InextensibleBackdoor.load(args.backdoor)
backdoor.check(algorithm)
rs = np.random.RandomState()
cg = CaseGenerator(algorithm, cnf, rs, backdoor)


mf_p["solver_wrapper"].check_installation()
with open(true_log_file, 'w+') as f:
    f.write("-- key generator: %s\n" % algorithm('').tag)
    f.write("-- solver: %s\n" % mf_p["solver_wrapper"].info["tag"])
    f.write("-- pf type: %s\n" % m_function.type)
    if m_function.type == "ibs":
        f.write("-- time limit: %s\n" % mf_p["time_limit"])
    f.write("-- samples size: %d\n" % mf_p["N"])
    f.write("-- backdoor: %s\n" % backdoor)
    f.write("------------------------------------------------------\n")

mf = m_function(mf_p)
result = mf.compute(cg)
value, mf_log = result[0], result[1]

with open(true_log_file, 'a') as f:
    f.write(mf_log + "true value: %.7g\n" % value)
