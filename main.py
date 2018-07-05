import sys

from util import constant, conclusion, configurator

if len(sys.argv) < 2:
    print "USAGE: main.py <log id> [conf path]"
    exit(1)

log_file = constant.log_path + sys.argv[1]
locals_log_file = constant.locals_log_path + sys.argv[1]
value_hash = {}

if len(sys.argv) >= 3:
    conf_path = sys.argv[2]
    alg, meta_p, mf_p = configurator.load(conf_path, value_hash)
else:
    alg, meta_p, mf_p = configurator.load_base(value_hash)

meta_p["log_file"] = log_file
meta_p["locals_log_file"] = locals_log_file
meta_p["value_hash"] = value_hash

with open(log_file, 'w+'):
    pass

alg = alg(meta_p)
locals_list = alg.start(mf_p)
conclusion.add_conclusion(log_file, alg.get_iteration_size(), alg.comparator, locals_list=locals_list)
