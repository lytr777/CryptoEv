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
parser.add_argument('backdoor', help='load backdoor from specified file')
parser.add_argument('-cp', metavar='tag/path', type=str, default="true", help='tag or path to configuration file')
parser.add_argument('-v', metavar='0', type=int, default=0, help='[0-3] verbosity level')
parser.add_argument('-d', '--description', metavar='test', default="", type=str, help='description for this launching')

args = parser.parse_args()
path, configuration = configurator.load(args.cp)
rc.configuration = configuration

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

solvers = configuration["solvers"]
for key in solvers.solvers.keys():
    solvers.get(key).check_installation()

cnf_path = static.cnfs[key_generator.tag]
rc.cnf = CnfParser().parse_for_path(cnf_path)

rc.case_generator = CaseGenerator(
    algorithm=key_generator,
    random_state=np.random.RandomState()
)

rc.logger.deferred_write("-- key generator: %s\n" % key_generator.tag)
rc.logger.deferred_write("-- solver: %s\n" % solvers.get("main").name)
rc.logger.deferred_write("-- pf type: %s\n" % predictive_f.type)
rc.logger.deferred_write("-- selection: %s\n" % predictive_f.selection)
rc.logger.deferred_write("-- backdoor: %s\n" % backdoor)
rc.logger.write("------------------------------------------------------\n")

c_out = predictive_f.compute(backdoor)
r = predictive_f.calculate(backdoor, c_out)
value, pf_log = r[0], r[1]

rc.logger.write(pf_log)
rc.logger.write("true value: %.7g\n" % value)

configuration["concurrency"].terminate()
configuration["output"].close()
