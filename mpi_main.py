import argparse
import numpy as np
from mpi4py import MPI

from constants import static
from model.case_generator import CaseGenerator
from util import conclusion
from configuration import configurator
from output.module.logger import Logger
from output.module.debugger import Debugger
from model.backdoor import SecretKey, Backdoor
from constants.runtime import runtime_constants as rc
from util.parse.cnf_parser import CnfParser

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
size = comm.Get_size()
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

backdoor = SecretKey(key_generator)
if args.backdoor is not None:
    with open(args.backdoor, 'r') as f:
        variables = [int(var) for var in f.readline().split(' ')]
        mask = [0] * backdoor.length
        for var in variables:
            mask[var - 1] = 1

        backdoor = backdoor.get_copy(mask)
        backdoor.check(key_generator)

for key in configuration["solvers"].solvers.keys():
    configuration["solvers"].get(key).check_installation()

if rank == 0:
    ri_list = np.random.randint(2 ** 32 - 1, size=size)
else:
    ri_list = []
ri_list = comm.bcast(ri_list, root=0)
rs = np.random.RandomState(ri_list[rank])

cnf_path = static.cnfs[key_generator.tag]
rc.cnf = CnfParser().parse_for_path(cnf_path)

rc.case_generator = CaseGenerator(
    random_state=rs,
    algorithm=key_generator,
)

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
