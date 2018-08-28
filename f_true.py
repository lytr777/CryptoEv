import argparse
import numpy as np

from configuration import configurator
from log_storage.logger import Logger
from model.case_generator import CaseGenerator
from model.backdoor import InextensibleBackdoor
from parse_utils.cnf_parser import CnfParser
from util import constant
from util.debugger import Debugger

parser = argparse.ArgumentParser(description='CryptoEv')
parser.add_argument('backdoor', help='load backdoor from specified file')
parser.add_argument('-cp', metavar='tag/path', type=str, default="true", help='tag or path to configuration file')
parser.add_argument('-v', metavar='0', type=int, default=0, help='[0-3] verbosity level')

args = parser.parse_args()
_, meta_p, pf_p, ls_p = configurator.load('true', {})
p_function = meta_p["predictive_function"]

ls_p["description"] = ""
ls_p["algorithm"] = pf_p["key_generator"].tag
logger = Logger(ls_p)

log_path = logger.get_log_path()

pf_p["debugger"] = Debugger(logger.get_debug_path(), args.v)
open(logger.get_debug_path(), 'w+').close()

algorithm = pf_p["key_generator"]
cnf_path = constant.cnfs[algorithm.tag]
cnf = CnfParser().parse_for_path(cnf_path)

backdoor = InextensibleBackdoor.load(args.backdoor)
backdoor.check(algorithm)
rs = np.random.RandomState()
cg = CaseGenerator(algorithm, cnf, rs)

pf_p["solver_wrapper"].check_installation()
with open(log_path, 'w+') as f:
    f.write("-- key generator: %s\n" % algorithm.tag)
    f.write("-- solver: %s\n" % pf_p["solver_wrapper"].info["tag"])
    f.write("-- pf type: %s\n" % p_function.type)
    if p_function.type == "ibs":
        f.write("-- time limit: %s\n" % pf_p["time_limit"])
    f.write("-- samples size: %d\n" % pf_p["N"])
    f.write("-- backdoor: %s\n" % backdoor)
    f.write("------------------------------------------------------\n")

mf = p_function(pf_p)
result = mf.compute(cg, backdoor)
value, pf_log = result[0], result[1]

with open(log_path, 'a') as f:
    f.write(pf_log + "true value: %.7g\n" % value)
logger.end()
