import argparse

from configuration import configurator
from log_storage.logger import Logger
from model.backdoor import SecretKey, InextensibleBackdoor
from util.debugger import Debugger
from util import conclusion

parser = argparse.ArgumentParser(description='CryptoEv')
parser.add_argument('-cp', metavar='tag/path', type=str, default="base", help='tag or path to configuration file')
parser.add_argument('-v', metavar='0', type=int, default=0, help='[0-3] verbosity level')
parser.add_argument('-b', '--backdoor', metavar='path', type=str, help='load backdoor from specified file')
parser.add_argument('-d', '--description', metavar='test', default="", type=str, help='description for this launching')
# parser.add_argument('-r', '--restore', help="try to restore by logs", action="store_true")

args = parser.parse_args()
alg, meta_p, pf_p, ls_p = configurator.load(args.cp, {})

ls_p["description"] = args.description
ls_p["algorithm"] = pf_p["key_generator"].tag
logger = Logger(ls_p)

meta_p["log_file"] = logger.get_log_path()
open(meta_p["log_file"], 'w+').close()
pf_p["debugger"] = Debugger(logger.get_debug_path(), args.v)
open(logger.get_debug_path(), 'w+').close()

if args.backdoor is None:
    meta_p["init_backdoor"] = SecretKey(pf_p["key_generator"])
else:
    meta_p["init_backdoor"] = InextensibleBackdoor.load(args.backdoor)
    meta_p["init_backdoor"].check(pf_p["key_generator"])

pf_p["solver_wrapper"].check_installation()

# if args.restore:

alg = alg(meta_p)
locals_list = alg.start(pf_p)
conclusion.add_conclusion({
    "path": meta_p["log_file"],
    "comparator": alg.comparator,
    "locals_list": locals_list
})
logger.end()
