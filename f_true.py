from util.options import predictive_function
from util import formatter, constant, configurator

value_hash = {}
_, _, mf_p = configurator.load('configurations/true.json', value_hash)
m_function = predictive_function["ibs"]

cases = [
    formatter.format_to_array("1110111111010000100011110001111111011000100101001110010000100000(32)")
]

with open(constant.true_log_path, 'w+') as f:
    f.write("-- Key Generator: %s\n" % mf_p["crypto_algorithm"])
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
    true_log += "value for mask %s: %.7g\n " % (formatter.format_array(cases[i]), values[i])

with open(constant.true_log_path, 'a') as f:
    f.write(true_log)
