import argparse
from mpi4py import MPI
from util.debugger import Debugger
from util import constant, conclusion, configurator

parser = argparse.ArgumentParser(description='CryptoEv')
parser.add_argument('id', type=str, help='suffix for log file')
parser.add_argument('-cp', metavar='file/path', type=str, default="configurations/base.json",
                    help='path to configuration file')
parser.add_argument('-v', metavar='0', type=int, default=0, help='[0-3] verbosity level')
parser.add_argument('-d', metavar='file/path', type=str, help='path to debug file')

args = parser.parse_args()
alg, meta_p, mf_p = configurator.load(args.cp, {}, True)

if "adaptive_N" in mf_p:
    raise Exception("MPI version not supported adaptive selection")

meta_p["log_file"] = constant.log_path + args.id
meta_p["locals_log_file"] = constant.locals_log_path + args.id

mf_p["debugger"] = Debugger(args.d, args.v)
if args.d is not None:
    open(args.d, 'w+').close()

mf_p["solver_wrapper"].check_installation()
open(meta_p["log_file"], 'w+').close()

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

alg = alg(meta_p, comm)
locals_list = alg.start(mf_p)
if rank == 0:
    conclusion.add_conclusion(meta_p["log_file"], alg.comparator, locals_list=locals_list)
