import sys

from util import constant, conclusion, configurator, parser, plotter

if len(sys.argv) < 2:
    print "USAGE: main.py <log id> [conf path]"
    exit(1)

log_file = constant.log_path + sys.argv[1]
locals_log_file = constant.locals_log_path + sys.argv[1]
value_hash = {}


# data_path = "./out/a5_1/02.05/log_%d.ibs.rokk.a5_1_log"
# data1 = parser.parse_out(data_path % 1, 2)
# data2 = parser.parse_out(data_path % 2, 2)
# data3 = parser.parse_out(data_path % 3, 2)
# data4 = parser.parse_out(data_path % 4, 2)
# data5 = parser.parse_out(data_path % 5, 2)
# data6 = parser.parse_out(data_path % 6, 2)
# data7 = parser.parse_out(data_path % 7, 2)
# data8 = parser.parse_out(data_path % 8, 2)
# plotter.show_plot([data1, data2, data3, data4, data5, data6, data7, data8], 111)
# exit(0)

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

# (1 + 1)
# 100 file: 28.04
# 50 file: 29.04
# 30 file: 30.04
# 20 file: 01.05
# 1-8 - 200 file: 02.05
#
# (1 + 2)
# 13-16

alg = alg(meta_p)
locals_list = alg.start(mf_p)
conclusion.add_conclusion(log_file, alg.get_iteration_size(), alg.comparator, locals_list=locals_list)
