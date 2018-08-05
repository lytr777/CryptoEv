import argparse

from configuration import configurator
from model.variable_set import SecretKey, Backdoor
from util.debugger import Debugger
from util import constant, conclusion

parser = argparse.ArgumentParser(description='CryptoEv')
parser.add_argument('id', type=str, help='suffix for log file')
parser.add_argument('-cp', metavar='tag/path', type=str, default="base", help='tag or path to configuration file')
parser.add_argument('-v', metavar='0', type=int, default=0, help='[0-3] verbosity level')
parser.add_argument('-d', metavar='path', type=str, help='path to debug file')
parser.add_argument('-b', '--backdoor', metavar='path', type=str, help='load backdoor from specified file')
# parser.add_argument('-r', '--restore', help="try to restore by logs", action="store_true")

args = parser.parse_args()
alg, meta_p, mf_p = configurator.load(args.cp, {})

meta_p["log_file"] = constant.log_path + args.id
meta_p["locals_log_file"] = constant.locals_log_path + args.id

mf_p["debugger"] = Debugger(args.d, args.v)
if args.d is not None:
    open(args.d, 'w+').close()

if args.backdoor is None:
    meta_p["init_backdoor"] = SecretKey(mf_p["key_generator"])
else:
    meta_p["init_backdoor"] = Backdoor.load(args.backdoor, mf_p["key_generator"])

mf_p["solver_wrapper"].check_installation()
open(meta_p["log_file"], 'w+').close()

# if args.restore:

alg = alg(meta_p)
locals_list = alg.start(mf_p)
conclusion.add_conclusion({
    "path": meta_p["log_file"],
    "comparator": alg.comparator,
    "locals_list": locals_list
})
