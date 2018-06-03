import sys

from util import constant, conclusion, configurator, parser, plotter

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

# # restore hash
# paths = [
#     ("./out/a5_1/01.05/log_%d.ibs.rokk.a5_1_log", 8, 2),
#     ("./out/a5_1/30.04/log_%d.ibs.rokk.a5_1_log", 8, 2),
#     ("./out/a5_1/29.04/log_%d.ibs.rokk.a5_1_log", 8, 2),
#     ("./out/a5_1/28.04/log_%d.ibs.rokk.a5_1_log", 8, 2),
#     ("./out/a5_1/02.05/log_%d.ibs.rokk.a5_1_log", 8, 2),
#     ("./out/a5_1/05.05/log_%d.ibs.rokk.a5_1_log", 4, 3),
#     ("./out/a5_1/08.05/log_%d.ibs.rokk.a5_1_log", 4, 6)
# ]
# for path, n, k in paths:
#     for i in range(n):
#         parser.restore_hash(value_hash, path % (i + 1), k)
#         print len(value_hash)
#
# tabu
# file 11.05

# 20.05 (1 + 1) with adaptive

alg = alg(meta_p)
locals_list = alg.start(mf_p)
conclusion.add_conclusion(log_file, alg.get_iteration_size(), alg.comparator, locals_list=locals_list)
