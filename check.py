from key_generators.volfram import Volfram
from solvers.case_solver import CaseSolver
from util import constant, caser, formatter, generator
from util.parser import parse_cnf
from wrapper.lingeling_in import LingelingInWrapper
from wrapper.treengeling import TreengelingWrapper

N = 20
base_cnf = parse_cnf(constant.volfram_cnf)

algorithm = Volfram

init_solver = LingelingInWrapper(constant.lingeling_path)
main_solver = TreengelingWrapper(constant.treengeling_path)

times = []
for i in range(N):
    print "---------- iteration %d ----------" % (i + 1)
    init_case = caser.create_init_case(base_cnf, algorithm)
    solver = CaseSolver(init_solver)
    solver.start({}, init_case)

    secret_key, key_stream = init_case.get_solution_secret_key(), init_case.get_solution_key_stream()
    print "init key stream: %s" % formatter.format_array(key_stream)
    print "init secret key: %s" % formatter.format_array(secret_key)

    parameters = {
        "key_stream": key_stream,
        # "secret_key": secret_key,
        # "secret_mask": generator.generate_mask(128, 64)
    }

    case = caser.create_case(base_cnf, parameters, algorithm)
    solver = CaseSolver(main_solver)
    solver.start({}, case)

    print "fond secret key: %s" % formatter.format_array(case.get_solution_secret_key())
    print "time: %s" % case.time
    times.append(case.time)

print "av_time: %s" % (sum(times) / N)
