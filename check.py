from solvers.case_solver import CaseSolver
from util import caser, formatter, options
from util.parser import parse_cnf

N = 20
workers = 4
algorithm = options.crypto_algorithms["volfram"]
base_cnf = parse_cnf(algorithm[1])
algorithm = algorithm[0]

init_solver = options.solver_wrappers["lingeling"]
main_solver = options.solver_wrappers["plingeling"]

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
    }

    case = caser.create_case(base_cnf, parameters, algorithm)
    solver = CaseSolver(main_solver)
    solver.start({"workers": workers}, case)

    print "fond secret key: %s" % formatter.format_array(case.get_solution_secret_key())
    print "time: %s" % case.time
    times.append(case.time)

print "av_time: %s" % (sum(times) / N)






