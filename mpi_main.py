import argparse
from mpi4py import MPI

from configuration import configurator
from util.debugger import Debugger
from util import constant, conclusion


parser = argparse.ArgumentParser(description='CryptoEv')
parser.add_argument('id', type=str, help='suffix for log file')
parser.add_argument('-cp', metavar='tag/path', type=str, default="base", help='tag or path to configuration file')
parser.add_argument('-v', metavar='0', type=int, default=0, help='[0-3] verbosity level')
parser.add_argument('-d', metavar='path', type=str, help='path to debug file')

args = parser.parse_args()
alg, meta_p, mf_p = configurator.load(args.cp, {}, True)

if "adaptive_N" in mf_p:
    raise Exception("MPI version not supported adaptive selection")

meta_p["log_file"] = constant.log_path + args.id
meta_p["locals_log_file"] = constant.locals_log_path + args.id

if args.v > 0 and args.d is None:
    raise Exception("MPI version support debug only with file")

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

if args.d is None:
    mf_p["debugger"] = Debugger(verb=args.v)
else:
    rank_debug_file = "%s_%d" % (args.d, rank)
    mf_p["debugger"] = Debugger(rank_debug_file, args.v)
    open(rank_debug_file, 'w+').close()

mf_p["solver_wrapper"].check_installation()
if rank == 0:
    open(meta_p["log_file"], 'w+').close()

alg = alg(meta_p, comm)
locals_list = alg.start(mf_p)
if rank == 0:
    conclusion.add_conclusion(meta_p["log_file"], alg.comparator, locals_list=locals_list)
