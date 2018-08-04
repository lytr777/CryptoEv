import argparse
import numpy as np

from configuration import configurator
from parse_utils.cnf_parser import CnfParser
from util import formatter, constant
from util.debugger import Debugger

parser = argparse.ArgumentParser(description='CryptoEv')
parser.add_argument('id', type=str, help='suffix for log file')
parser.add_argument('backdoor', help='load backdoor from specified file')
parser.add_argument('-cp', metavar='tag/path', type=str, default="true", help='tag or path to configuration file')
parser.add_argument('-v', metavar='0', type=int, default=0, help='[0-3] verbosity level')
parser.add_argument('-d', metavar='path', type=str, help='path to debug file')

args = parser.parse_args()
_, meta_p, mf_p = configurator.load('true', {})
m_function = meta_p["predictive_function"]

true_log_file = constant.true_log_path + args.id

mf_p["debugger"] = Debugger(args.d, args.v)
if args.d is not None:
    open(args.d, 'w+').close()

algorithm, cnf_path = mf_p["crypto_algorithm"]
cnf = CnfParser().parse_for_path(cnf_path)
mf_p["crypto_algorithm"] = (algorithm, cnf, cnf_path)

case = np.zeros(algorithm.secret_key_len)
with open(args.backdoor, 'r') as f:
    var_list = f.readline().split(' ')
    for var in var_list:
        case[int(var) - 1] = 1

with open(true_log_file, 'w+') as f:
    f.write("-- Key Generator: %s\n" % mf_p["crypto_algorithm"][0](''))
    f.write("-- N = %d\n" % mf_p["N"])
    f.write("------------------------------------------------------\n")
    f.write("start with mask: %s\n" % formatter.format_array(case))

mf = m_function(mf_p)
result = mf.compute(case)
value, mf_log = result[0], result[1]

with open(true_log_file, 'a') as f:
    f.write(mf_log + "true value: %.7g\n" % value)
