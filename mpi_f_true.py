import argparse
import numpy as np
from mpi4py import MPI
from time import time as now

from constants import static
from model.backdoor import Backdoor
from configuration import configurator
from output.module.logger import Logger
from output.module.debugger import Debugger
from model.case_generator import CaseGenerator
from constants.runtime import runtime_constants as rc
from util.parse.cnf_parser import CnfParser

parser = argparse.ArgumentParser(description='CryptoEv')
parser.add_argument('backdoor', help='load backdoor from specified file')
parser.add_argument('-cp', metavar='tag/path', type=str, default="true", help='tag or path to configuration file')
parser.add_argument('-v', metavar='0', type=int, default=0, help='[0-3] verbosity level')
parser.add_argument('-d', '--description', metavar='test', default="", type=str, help='description for this launching')

parser.add_argument('-md', '--mpi_debug', metavar='0', type=bool, default=False, help='debug file for all nodes')

args = parser.parse_args()
path, configuration = configurator.load(args.cp, mpi=True)
rc.configuration = configuration

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

predictive_f = rc.configuration["predictive_function"]
key_generator = predictive_f.key_generator
# output
if rank == 0:
    output = configuration["output"]
    output.create(
        key_generator=key_generator.tag,
        description=args.description,
        conf_path=path,
    )

    rc.logger = Logger(output.get_log_path())
    rc.debugger = Debugger(output.get_debug_path(), args.v)

if args.mpi_debug:
    df = rc.debugger.debug_file if rank == 0 else ""
    df = comm.bcast(df, root=0)
    if rank != 0:
        rc.debugger = Debugger("%s_%d" % (df, rank), args.v)

backdoor = Backdoor.load(args.backdoor)
backdoor.check(key_generator)

for key in configuration["solvers"].solvers.keys():
    configuration["solvers"].get(key).check_installation()

# --
cnf_path = static.cnfs[key_generator.tag]
cnf = CnfParser().parse_for_path(cnf_path)
rs = np.random.RandomState(43)

cg = CaseGenerator(key_generator, cnf, rs)

if rank == 0:
    rc.logger.deferred_write("-- key generator: %s\n" % key_generator.tag)
    rc.logger.deferred_write("-- selection: %s\n" % predictive_f.selection)
    rc.logger.deferred_write("-- backdoor: %s\n" % backdoor)
    rc.logger.write("------------------------------------------------------\n")

predictive_f.selection.set_mpi_sett(size, rank)

if rank == 0:
    start_work_time = now()
    c_out = predictive_f.compute(cg, backdoor)

    cases = comm.gather(c_out[0], root=0)
    cases = np.concatenate(cases)

    time = now() - start_work_time
    r = predictive_f.calculate(cg, backdoor, (cases, time))

    value, pf_log = r[0], r[1]
    rc.logger.write(pf_log)
    rc.logger.write("true value: %.7g\n" % value)
    configuration["output"].close()
else:
    c_out = predictive_f.compute(cg, backdoor)
    cases = comm.gather(c_out[0], root=0)

configuration["concurrency"].terminate()
