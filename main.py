import argparse

from configuration import configurator

from util import conclusion
from output.module.logger import Logger
from output.module.debugger import Debugger
from model.backdoor import SecretKey, Backdoor
from constants.runtime import runtime_constants as rc

parser = argparse.ArgumentParser(description='CryptoEv')
parser.add_argument('-cp', metavar='tag/path', type=str, default="base", help='tag or path to configuration file')
parser.add_argument('-v', metavar='0', type=int, default=0, help='[0-3] verbosity level')
parser.add_argument('-b', '--backdoor', metavar='path', type=str, help='load backdoor from specified file')
parser.add_argument('-d', '--description', metavar='test', default="", type=str, help='description for this launching')
# parser.add_argument('-r', '--restore', help="try to restore by logs", action="store_true")

args = parser.parse_args()
path, configuration = configurator.load(args.cp)
rc.configuration = configuration

key_generator = configuration["predictive_function"].key_generator
# output
output = configuration["output"]
output.create(
    key_generator=key_generator.tag,
    description=args.description,
    conf_path=path
)

rc.logger = Logger(output.get_log_path())
rc.debugger = Debugger(output.get_debug_path(), args.v)

if args.backdoor is None:
    backdoor = SecretKey(key_generator)
else:
    backdoor = Backdoor.load(args.backdoor)
    backdoor.check(key_generator)

for key in configuration["solvers"].solvers.keys():
    configuration["solvers"].get(key).check_installation()

# if args.restore:

algorithm = configuration["algorithm"]
rc.logger.write(algorithm.get_info())
locals_list = algorithm.start(backdoor)

conclusion.add_conclusion({
    "path": rc.logger.log_file,
    "comparator": algorithm.comparator,
    "locals_list": locals_list
})
configuration["concurrency"].terminate()
configuration["output"].close()
