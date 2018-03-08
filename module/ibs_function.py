import numpy as np

from module.multi_case_solver import MultiCaseSolver
from util import caser
from util.parser import parse_cnf
from time import time as now


class IBSFunction:
    def __init__(self, parameters):
        self.crypto_algorithm = parameters["crypto_algorithm"]
        self.cnf_link = parameters["cnf_link"]
        self.N = parameters["N"]
        self.current_solver = parameters["solver_wrapper"]
        self.time_limit = parameters["time_limit"]
        self.thread_count = parameters["threads"] if ("threads" in parameters) else 1

        self.base_cnf = parse_cnf(self.cnf_link)

    def compute(self, mask):
        # init
        cases = []

        for i in range(self.N):
            cases.append(caser.create_init_case(self.base_cnf, self.crypto_algorithm))

        solver_args = {
            "subprocess_thread": self.thread_count
        }

        multi_solver = MultiCaseSolver(self.current_solver, verbosity=False)
        init_start_time = now()
        solved_init_cases, broken_int_cases = multi_solver.start(solver_args, cases)

        if len(broken_int_cases) != 0:
            print "count of broken cases in init phase not equals zero!"
            exit(0)
        else:
            print "init phase ended with time: " + str(now() - init_start_time)

        # compute
        cases = []

        parameters = {
            "secret_mask": mask
        }

        for init_case in solved_init_cases:
            parameters["secret_key"] = init_case.get_solution_secret_key()
            parameters["key_stream"] = init_case.get_solution_key_stream()

            cases.append(caser.create_case(self.base_cnf, parameters, self.crypto_algorithm))

        solver_args["time_limit"] = self.time_limit

        multi_solver = MultiCaseSolver(self.current_solver)
        solved_cases, broken_cases = multi_solver.start(solver_args, cases)

        time_stat = {
            "DETERMINATE": 0,
            "INDETERMINATE": 0
        }

        flags_stat = {
            "PREPROCESSING": 0,
            "PROCESSING": 0
        }

        for case in solved_cases:
            self.__update_time_statistic(time_stat, case.status)
            self.__update_flags_statistic(flags_stat, case.flags)

        xi = time_stat["DETERMINATE"] / len(solved_cases)
        value = (2 ** np.count_nonzero(mask)) * self.time_limit * (3 / xi)

        return value, [time_stat, flags_stat]

    def __update_time_statistic(self, time_stat, status):
        if status == "UNSATISFIABLE" or status == "SATISFIABLE":
            time_stat["DETERMINATE"] += 1
        else:
            time_stat["INDETERMINATE"] += 1

    def __update_flags_statistic(self, flags_stat, flags):
        if flags[0]:
            flags_stat["PREPROCESSING"] += 1
        else:
            flags_stat["PROCESSING"] += 1