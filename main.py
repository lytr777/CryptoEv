import argparse
import numpy as np

from configuration import configurator
from constants import static
from model.case_generator import CaseGenerator

from util import conclusion
from output.module.logger import Logger
from output.module.debugger import Debugger
from model.backdoor import SecretKey, Backdoor
from constants.runtime import runtime_constants as rc
from util.parse.cnf_parser import CnfParser

parser = argparse.ArgumentParser(description='CryptoEv')
parser.add_argument('keygen', type=str, help='key generator')
parser.add_argument('-cp', metavar='tag/path', type=str, default="base", help='tag or path to configuration file')
parser.add_argument('-v', metavar='0', type=int, default=0, help='[0-3] verbosity level')
parser.add_argument('-b', '--backdoor', metavar='path', type=str, help='load backdoor from specified file')
parser.add_argument('-d', '--description', metavar='str', default="", type=str, help='experiment description')
# parser.add_argument('-r', '--restore', help="try to restore by logs", action="store_true")

args = parser.parse_args()
path, configuration = configurator.load(args.cp)
key_generator = configurator.get_key_generator(args.keygen)
rc.configuration = configuration

# output
output = configuration["output"]
output.create(
    key_generator=key_generator.tag,
    description=args.description,
    conf_path=path
)

rc.logger = Logger(output.get_log_path())
rc.debugger = Debugger(output.get_debug_path(), args.v)

# backdoor
if args.backdoor is None:
    backdoor = SecretKey(key_generator)
else:
    backdoor = Backdoor.load(args.backdoor)[0]
    # backdoor.check(key_generator)

# solvers
solvers = configuration["solvers"]
for solver in solvers:
    solver.check_installation()

# case_generator
cnf_path = static.cnfs[key_generator.tag]
rc.cnf = CnfParser().parse_for_path(cnf_path)

rc.case_generator = CaseGenerator(
    algorithm=key_generator,
    random_state=np.random.RandomState()
)

algorithm = configuration["algorithm"]
predictive_f = rc.configuration["predictive_function"]
# print header
rc.logger.write(algorithm.get_info())
rc.logger.deferred_write("-- key generator: %s\n" % args.keygen)
rc.logger.deferred_write("-- %s\n" % solvers)
rc.logger.deferred_write("-- pf type: %s\n" % predictive_f.type)
rc.logger.deferred_write("-- time limit: %s\n" % solvers.get_tl("main"))
rc.logger.deferred_write("-- selection: %s\n" % predictive_f.selection)
rc.logger.write("------------------------------------------------------\n")

locals_list = algorithm.start(backdoor)

conclusion.add_conclusion({
    "path": rc.logger.log_file,
    "comparator": algorithm.comparator,
    "locals_list": locals_list
})

configuration["concurrency"].terminate()
configuration["output"].close()
