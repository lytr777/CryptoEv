import argparse
import numpy as np
from mpi4py import MPI

from util import conclusion
from configuration import configurator
from output.module.logger import Logger
from output.module.debugger import Debugger
from model.backdoor import SecretKey, Backdoor
from constants.runtime import runtime_constants as rc

parser = argparse.ArgumentParser(description='CryptoEv')
parser.add_argument('-cp', metavar='tag/path', type=str, default="base", help='tag or path to configuration file')
parser.add_argument('-v', metavar='0', type=int, default=0, help='[0-3] verbosity level')
parser.add_argument('-b', '--backdoor', metavar='path', type=str, help='load backdoor from specified file')
parser.add_argument('-d', '--description', metavar='test', default="", type=str, help='description for this launching')

parser.add_argument('-md', '--mpi_debug', metavar='0', type=bool, default=False, help='debug file for all nodes')

args = parser.parse_args()
path, configuration = configurator.load(args.cp, mpi=True)
rc.configuration = configuration

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

key_generator = configuration["predictive_function"].key_generator
# output
if rank == 0:
    output = configuration["output"]
    output.create(
        key_generator=key_generator.tag,
        description=args.description,
        conf_path=path
    )

    rc.logger = Logger(output.get_log_path())
    rc.debugger = Debugger(output.get_debug_path(), args.v)

if args.mpi_debug:
    df = rc.debugger.debug_file if rank == 0 else ""
    df = comm.bcast(df, root=0)
    if rank != 0:
        rc.debugger = Debugger("%s_%d" % (df, rank), args.v)


if args.backdoor is None:
    backdoor = SecretKey(key_generator)
else:
    backdoor = Backdoor.load(args.backdoor)
    backdoor.check(key_generator)

for key in configuration["solvers"].solvers.keys():
    configuration["solvers"].get(key).check_installation()

# for test
# !!!!
for i in range(1, 102, 10):
    if rank == 0:
        rc.debugger.write(2, 1, "sending array for test ... %d" % i)
        bbb = np.empty(i, dtype=int)
    else:
        bbb = None
    bbb = comm.bcast(bbb, root=0)
    if rank != 0:
        rc.debugger.write(2, 1, "receive array for test ... %d" % i)
# !!!!
# for test

algorithm = configuration["algorithm"]
if rank == 0:
    rc.logger.write(algorithm.get_info())
locals_list = algorithm.start(backdoor)

if rank == 0:
    conclusion.add_conclusion({
        "path": rc.logger.log_file,
        "comparator": algorithm.comparator,
        "locals_list": locals_list
    })
    configuration["output"].close()
configuration["concurrency"].terminate()
