import numpy as np

from util import caser
from util.parser import parse_cnf
from time import time as now


class IBSFunction:
    def __init__(self, parameters):
        self.crypto_algorithm = parameters["crypto_algorithm"]
        self.N = parameters["N"]
        self.multi_solver = parameters["multi_solver"]
        self.current_solver = parameters["solver_wrapper"]
        self.time_limit = parameters["time_limit"]
        self.corrector = parameters["corrector"] if ("corrector" in parameters) else None
        self.thread_count = parameters["threads"] if ("threads" in parameters) else 1

        self.base_cnf = parse_cnf(self.crypto_algorithm[1])
        self.log = ""

    def compute(self, mask):
        # init
        cases = []

        for i in range(self.N):
            cases.append(caser.create_init_case(self.base_cnf, self.crypto_algorithm[0]))

        solver_args = {
            "subprocess_thread": self.thread_count
        }

        self.current_solver.set_simplifying(False)
        m_solver = self.multi_solver(self.current_solver)
        init_start_time = now()
        solved_init_cases, broken_init_cases, _ = m_solver.start(solver_args, cases)

        if len(broken_init_cases) != 0:
            print "Count of broken cases in init phase not equals zero!"
            exit(0)
        else:
            self.log += "init phase ended with time: %f\n" % (now() - init_start_time)

        # compute
        cases = []

        parameters = {
            "secret_mask": mask
        }

        for init_case in solved_init_cases:
            parameters["secret_key"] = init_case.get_solution_secret_key()
            parameters["key_stream"] = init_case.get_solution_key_stream()

            cases.append(caser.create_case(self.base_cnf, parameters, self.crypto_algorithm[0]))

        solver_args["time_limit"] = self.time_limit

        self.current_solver.set_simplifying(True)
        m_solver = self.multi_solver(self.current_solver)
        main_start_time = now()
        solved_cases, broken_cases, solver_log = m_solver.start(solver_args, cases)
        self.log += solver_log
        self.log += "main phase ended with time: %f\n" % (now() - main_start_time)

        if len(broken_init_cases) != 0:
            print "Some cases is broken in IBS method!"
            exit(0)

        time_stat = {
            "DETERMINATE": 0,
            "INDETERMINATE": 0
        }

        flags_stat = {
            "PREPROCESSING": 0,
            "PROCESSING": 0
        }

        if self.corrector is not None:
            self.time_limit = self.corrector(solved_cases, self.time_limit)
            self.log += "time limit has been corrected: %f" % self.time_limit
            time_stat["DISCARDED"] = 0

        for case in solved_cases:
            self.__update_time_statistic(time_stat, case.status)
            self.__update_flags_statistic(flags_stat, case.flags)

        xi = float(time_stat["DETERMINATE"]) / float(len(solved_cases))
        if xi != 0:
            value = (2 ** np.count_nonzero(mask)) * self.time_limit * (3 / xi)
        else:
            value = (2 ** self.crypto_algorithm[0].secret_key_len) * self.time_limit

        self.log += "%s\n" % time_stat
        self.log += "%s\n" % flags_stat
        return value, self.log

    @staticmethod
    def __update_time_statistic(time_stat, status):
        if status == "UNSATISFIABLE" or status == "SATISFIABLE":
            time_stat["DETERMINATE"] += 1
        elif status == "DISCARDED":
            time_stat["DISCARDED"] += 1
        else:
            time_stat["INDETERMINATE"] += 1

    @staticmethod
    def __update_flags_statistic(flags_stat, flags):
        if flags[0]:
            flags_stat["PREPROCESSING"] += 1
        else:
            flags_stat["PROCESSING"] += 1
