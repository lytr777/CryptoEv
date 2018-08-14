import argparse
import numpy as np
from mpi4py import MPI
from time import time as now

from configuration import configurator
from log_storage.logger import Logger
from model.case_generator import CaseGenerator
from model.backdoor import InextensibleBackdoor
from parse_utils.cnf_parser import CnfParser
from util import constant
from util.debugger import Debugger, DebuggerStub

parser = argparse.ArgumentParser(description='CryptoEv')
parser.add_argument('backdoor', help='load backdoor from specified file')
parser.add_argument('-cp', metavar='tag/path', type=str, default="true", help='tag or path to configuration file')
parser.add_argument('-v', metavar='0', type=int, default=0, help='[0-3] verbosity level')

args = parser.parse_args()
_, meta_p, pf_p, ls_p = configurator.load('true', {})
p_function = meta_p["predictive_function"]

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    ls_p["description"] = ""
    ls_p["algorithm"] = pf_p["key_generator"].tag
    logger = Logger(ls_p)

    log_path = logger.get_log_path()
    pf_p["debugger"] = Debugger(logger.get_debug_path(), args.v)
    open(logger.get_debug_path(), 'w+').close()
else:
    meta_p["log_file"] = ''
    pf_p["debugger"] = DebuggerStub()

algorithm = pf_p["key_generator"]
cnf_path = constant.cnfs[algorithm.tag]
cnf = CnfParser().parse_for_path(cnf_path)

backdoor = InextensibleBackdoor.load(args.backdoor)
backdoor.check(algorithm)
rs = np.random.RandomState()
cg = CaseGenerator(algorithm, cnf, rs, backdoor)

pf_p["solver_wrapper"].check_installation()
if rank == 0:
    with open(log_path, 'w+') as f:
        f.write("-- key generator: %s\n" % algorithm.tag)
        f.write("-- solver: %s\n" % pf_p["solver_wrapper"].info["tag"])
        f.write("-- pf type: %s\n" % p_function.type)
        if p_function.type == "ibs":
            f.write("-- time limit: %s\n" % pf_p["time_limit"])
        f.write("-- samples size: %d\n" % pf_p["N"])
        f.write("-- backdoor: %s\n" % backdoor)
        f.write("------------------------------------------------------\n")

pf_p["mpi_call"] = True

quotient, remainder = divmod(pf_p["N"], size)
rank_N = quotient + (1 if remainder > 0 else 0)
real_N = rank_N * size

pf_p["N"] = rank_N

if rank == 0:
    start_work_time = now()

    pf = p_function(pf_p)
    result = pf.compute(cg)

    cases = comm.gather(result[2], root=0)
    cases = np.concatenate(cases)

    time = now() - start_work_time
    final_result = pf.handle_cases(cg, cases, time)
    value, pf_log = final_result[0], final_result[1]

    with open(log_path, 'a') as f:
        f.write(pf_log + "true value: %.7g\n" % value)
    logger.end()
else:
    pf = p_function(pf_p)
    result = pf.compute(cg)

    comm.gather(result[2], root=0)
