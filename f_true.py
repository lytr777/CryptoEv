import argparse

from configuration import configurator
from parse_utils.cnf_parser import CnfParser
from util import formatter, constant
from util.debugger import Debugger

cases = [
    formatter.format_to_array("1110111111010000100011110001111111011000100101001110010000100000(32)")
]

parser = argparse.ArgumentParser(description='CryptoEv')
parser.add_argument('id', type=str, help='suffix for log file')
parser.add_argument('-cp', metavar='tag/path', type=str, default="true", help='tag or path to configuration file')
parser.add_argument('-v', metavar='0', type=int, default=0, help='[0-3] verbosity level')
parser.add_argument('-d', metavar='path', type=str, help='path to debug file')

args = parser.parse_args()
_, meta_p, mf_p = configurator.load('true', {})
m_function = meta_p["predictive_function"]

mf_p["debugger"] = Debugger(args.d, args.v)
if args.d is not None:
    open(args.d, 'w+').close()

algorithm, cnf_path = mf_p["crypto_algorithm"]
cnf = CnfParser().parse_for_path(cnf_path)
mf_p["crypto_algorithm"] = (algorithm, cnf, cnf_path)

with open(constant.true_log_path, 'w+') as f:
    f.write("-- Key Generator: %s\n" % mf_p["crypto_algorithm"][0](''))
    f.write("-- N = %d\n" % mf_p["N"])
    f.write("------------------------------------------------------\n")

values = []
for case in cases:
    with open(constant.true_log_path, 'a') as f:
        f.write("start with mask: %s\n" % formatter.format_array(case))
    mf = m_function(mf_p)
    result = mf.compute(case)
    value, mf_log = result[0], result[1]
    values.append(value)

    log = mf_log
    log += "true value: %.7g\n" % value
    log += "------------------------------------------------------\n"

    with open(constant.true_log_path, 'a') as f:
        f.write(log)

true_log = "------------------------------------------------------\n"
true_log += "------------------------------------------------------\n"
for i in range(len(cases)):
    true_log += "value for mask %s: %.7g\n" % (formatter.format_array(cases[i]), values[i])

with open(constant.true_log_path, 'a') as f:
    f.write(true_log)
