import argparse
import numpy as np

from configuration import configurator
from constants import static

from output.module.debugger import Debugger
from output.module.logger import Logger
from constants.runtime import runtime_constants as rc
from model.case_generator import CaseGenerator
from model.backdoor import Backdoor
from util.parse.cnf_parser import CnfParser

parser = argparse.ArgumentParser(description='CryptoEv')
parser.add_argument('keygen', type=str, help='key generator')
parser.add_argument('backdoor', type=str, help='load backdoor from specified file')
parser.add_argument('-cp', metavar='tag/path', type=str, default="true", help='tag or path to configuration file')
parser.add_argument('-v', metavar='0', type=int, default=0, help='[0-3] verbosity level')
parser.add_argument('-d', '--description', metavar='str', default="", type=str, help='experiment description')

args = parser.parse_args()
path, configuration = configurator.load(args.cp)
key_generator = configurator.get_key_generator(args.keygen)
rc.configuration = configuration

# output
output = configuration["output"]
output.create(
    key_generator=key_generator.tag,
    description=args.description,
    conf_path=path,
)

# backdoor
backdoors = Backdoor.load(args.backdoor)
for backdoor in backdoors:
    backdoor.check(key_generator)

# solvers
solvers = configuration["solvers"]
for solver in solvers:
    solver.check_installation()

# case generator
cnf_path = static.cnfs[key_generator.tag]
rc.cnf = CnfParser().parse_for_path(cnf_path)

rc.case_generator = CaseGenerator(
    algorithm=key_generator,
    random_state=np.random.RandomState()
)

for i in range(len(backdoors)):
    rc.logger = Logger('%s_%d' % (output.get_log_path(), i))
    rc.debugger = Debugger('%s_%d' % (output.get_debug_path(), i), args.v)

    predictive_f = rc.configuration["predictive_function"]
    # print header
    rc.logger.deferred_write("-- key generator: %s\n" % args.keygen)
    rc.logger.deferred_write("-- %s\n" % solvers)
    rc.logger.deferred_write("-- pf type: %s\n" % predictive_f.type)
    rc.logger.deferred_write("-- time limit: %s\n" % solvers.get_tl("main"))
    rc.logger.deferred_write("-- selection: %s\n" % predictive_f.selection)
    rc.logger.deferred_write("-- backdoor: %s\n" % backdoors[i])
    rc.logger.write("------------------------------------------------------\n")

    c_out = predictive_f.compute(backdoors[i])
    r = predictive_f.calculate(backdoors[i], c_out)
    value, pf_log = r[0], r[1]

    rc.logger.write(pf_log)
    rc.logger.write("true value: %.7g\n" % value)
    i += 1

configuration["concurrency"].terminate()
configuration["output"].close()
