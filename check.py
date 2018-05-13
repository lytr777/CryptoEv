from solvers.case_solver import CaseSolver
from util import caser, formatter, options
from util.parser import parse_cnf

N = 20
workers = 32
algorithm = options.crypto_algorithms["geffe"]
base_cnf = parse_cnf(algorithm[1])
algorithm = algorithm[0]

init_solver = options.solver_wrappers["lingeling"]
main_solver = options.solver_wrappers["treengeling"]

with open('out/check.data', 'w+'):
    pass

times = []
for i in range(N):
    log = "---------- iteration %d ----------\n" % (i + 1)
    init_case = caser.create_init_case(base_cnf, algorithm)
    solver = CaseSolver(init_solver)
    solver.start({}, init_case)

    secret_key, key_stream = init_case.get_solution_secret_key(), init_case.get_solution_key_stream()
    log += "init key stream: %s\n" % formatter.format_array(key_stream)
    log += "init secret key: %s\n" % formatter.format_array(secret_key)

    parameters = {
        "key_stream": key_stream,
    }

    case = caser.create_case(base_cnf, parameters, algorithm)
    solver = CaseSolver(main_solver)
    solver.start({"workers": workers}, case)

    log += "fond secret key: %s\n" % formatter.format_array(case.get_solution_secret_key())
    log += "time: %s\n" % case.time
    times.append(case.time)

    with open('out/check.data', 'a') as f:
        f.write(log)

with open('out/check.data', 'a') as f:
    f.write("av_time: %s\n" % (sum(times) / N))






