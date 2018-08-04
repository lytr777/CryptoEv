import argparse
import numpy as np
from mpi4py import MPI
from time import time as now

from configuration import configurator
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

algorithm, cnf_path = mf_p["crypto_algorithm"]
cnf = CnfParser().parse_for_path(cnf_path)
mf_p["crypto_algorithm"] = (algorithm, cnf, cnf_path)

case = np.zeros(algorithm.secret_key_len)
with open(args.backdoor, 'r') as f:
    var_list = f.readline().split(' ')
    for var in var_list:
        case[int(var) - 1] = 1

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if args.d is None:
    mf_p["debugger"] = Debugger(verb=args.v)
else:
    rank_debug_file = "%s_%d" % (args.d, rank)
    mf_p["debugger"] = Debugger(rank_debug_file, args.v)
    open(rank_debug_file, 'w+').close()

mf_p["solver_wrapper"].check_installation()
if rank == 0:
    with open(true_log_file, 'w+') as f:
        f.write("-- Key Generator: %s\n" % mf_p["crypto_algorithm"][0](''))
        f.write("-- N = %d\n" % mf_p["N"])
        f.write("------------------------------------------------------\n")
        f.write("start with mask: %s\n" % formatter.format_array(case))

mf_p["mpi_call"] = True

(quotient, remainder) = divmod(mf_p["N"], size)
rank_N = quotient + (1 if remainder > 0 else 0)
real_N = rank_N * size

mf_p["N"] = rank_N

if rank == 0:
    start_work_time = now()

    mf = m_function(mf_p)
    result = mf.compute(case)

    cases = comm.gather(result[2], root=0)
    cases = np.concatenate(cases)

    time = now() - start_work_time
    final_result = mf.handle_cases(case, cases, time)
    value, mf_log = final_result[0], final_result[1]

    with open(true_log_file, 'a') as f:
        f.write(mf_log + "true value: %.7g\n" % value)
else:
    mf = m_function(mf_p)
    result = mf.compute(case)

    comm.gather(result[2], root=0)
