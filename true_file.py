import os
import argparse
from multiprocessing import Pool

import numpy as np
from time import time as now

from configuration import configurator
from constants import static

from output.module.debugger import Debugger
from output.module.logger import Logger
from constants.runtime import runtime_constants as rc
from model.case_generator import CaseGenerator
from model.backdoor import Backdoor
from true.task_reader import TaskReader
from true.task_writer import TaskWriter
from util.parse.cnf_parser import CnfParser

parser = argparse.ArgumentParser(description='CryptoEv')
parser.add_argument('backdoor', help='load backdoor from specified file')
parser.add_argument('-cp', metavar='tag/path', type=str, default="true", help='tag or path to configuration file')
parser.add_argument('-v', metavar='0', type=int, default=0, help='[0-3] verbosity level')
parser.add_argument('-d', '--description', metavar='test', default="", type=str, help='description for this launching')

args = parser.parse_args()
path, configuration = configurator.load(args.cp)
rc.configuration = configuration

chuck_size = 20

predictive_f = rc.configuration["predictive_function"]
key_generator = predictive_f.key_generator
# output
output = configuration["output"]
output.create(
    key_generator=key_generator.tag,
    description=args.description,
    conf_path=path,
)

rc.logger = Logger(output.get_log_path())
rc.debugger = Debugger(output.get_debug_path(), args.v)

backdoor = Backdoor.load(args.backdoor)
backdoor.check(key_generator)

for key in configuration["solvers"].solvers.keys():
    configuration["solvers"].get(key).check_installation()

# --
cnf_path = static.cnfs[key_generator.tag]
cnf = CnfParser().parse_for_path(cnf_path)
rs = np.random.RandomState()

cg = CaseGenerator(key_generator, cnf, rs)

rc.logger.deferred_write("-- key generator: %s\n" % key_generator.tag)
rc.logger.deferred_write("-- selection: %s\n" % predictive_f.selection)
rc.logger.deferred_write("-- backdoor: %s\n" % backdoor)
rc.logger.write("------------------------------------------------------\n")

rc.debugger.write(0, 0, "Preparing instances for evaluating...")
prep_start_time = now()

N = rc.configuration["predictive_function"].selection.get_N()
file_count, remainder = divmod(N, chuck_size)
if remainder != 0:
    raise Exception("Remainder not equals zero")

rc.debugger.write(0, 0, "Samples count: %d" % N)
rc.debugger.write(0, 0, "Will be created %d files" % file_count)
rc.debugger.write(0, 0, "Each file will contain %d instances" % chuck_size)

tw = TaskWriter(chuck_size=chuck_size, cg=cg, backdoor=backdoor)


def tw_write(tw_args):
    path_j, init_cases = tw_args
    return tw.write(path_j, init_cases)


solvers = rc.configuration["solvers"]
concurrency = rc.configuration["concurrency"]
pool = Pool(processes=concurrency.thread_count)

ress, files = [], []
for i in range(file_count):
    path_i = "./_tmp/chunk_%d" % i
    ic = tw.prepare()
    res = pool.apply_async(tw_write, ((path_i, ic),))
    ress.append(res)

while len(ress) > 0:
    ress[0].wait()

    i = 0
    while i < len(ress):
        if ress[i].ready():
            res = ress.pop(i)
            files.append(res.get())
        else:
            i += 1

pool.terminate()
rc.debugger.write(0, 0, "Preparing completed in time: %f" % (now() - prep_start_time))

tr = TaskReader(cg=cg, backdoor=backdoor)

cases, times = [], []
for path_i in files:
    tasks = tr.read(path_i)
    rc.debugger.write(0, 0, "Loaded file %s with %d instances" % (path_i, len(tasks)))

    rc.debugger.deferred_write(1, 0, "compute for backdoor: %s" % backdoor)
    rc.debugger.deferred_write(1, 0, "use time limit: %s" % solvers.get_tl("main"))

    rc.debugger.write(1, 0, "solving...")
    solved, time = concurrency.solve(tasks)

    rc.debugger.deferred_write(1, 0, "has been solved %d cases" % len(solved))
    rc.debugger.write(1, 0, "spent time: %f" % time)

    cases.extend(solved)
    times.append(time)

r = predictive_f.calculate(cg, backdoor, (cases, sum(times)))
value, pf_log = r[0], r[1]

rc.logger.write(pf_log)
rc.logger.write("true value: %.7g\n" % value)

# tw.clean(*files)
configuration["concurrency"].terminate()
configuration["output"].close()

