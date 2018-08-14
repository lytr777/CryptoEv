import argparse
import numpy as np
from mpi4py import MPI
from time import time as now

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
_, meta_p, pf_p, ls_p = configurator.load('true', {})
p_function = meta_p["predictive_function"]

true_log_file = constant.true_log_path + args.id

algorithm = pf_p["key_generator"]
cnf_path = constant.cnfs[algorithm.tag]
cnf = CnfParser().parse_for_path(cnf_path)

backdoor = InextensibleBackdoor.load(args.backdoor)
backdoor.check(algorithm)
rs = np.random.RandomState()
cg = CaseGenerator(algorithm, cnf, rs, backdoor)

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if args.d is None:
    pf_p["debugger"] = Debugger(verb=args.v)
else:
    rank_debug_file = "%s_%d" % (args.d, rank)
    pf_p["debugger"] = Debugger(rank_debug_file, args.v)
    open(rank_debug_file, 'w+').close()

pf_p["solver_wrapper"].check_installation()
if rank == 0:
    with open(true_log_file, 'w+') as f:
        f.write("-- key generator: %s\n" % algorithm('').tag)
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

    with open(true_log_file, 'a') as f:
        f.write(pf_log + "true value: %.7g\n" % value)
else:
    pf = p_function(pf_p)
    result = pf.compute(cg)

    comm.gather(result[2], root=0)
