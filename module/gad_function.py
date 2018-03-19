import numpy as np

from module.case_solver import CaseSolver
from util import caser, generator
from util.formatter import format_array
from util.parser import parse_cnf


class GADFunction:
    def __init__(self, parameters, solution_key_stream=None):
        self.crypto_algorithm = parameters["crypto_algorithm"]
        self.cnf_link = parameters["cnf_link"]
        self.N = parameters["N"]
        self.multi_solver = parameters["multi_solver"]
        self.current_solver = parameters["solver_wrapper"]
        self.thread_count = parameters["threads"] if ("threads" in parameters) else 1
        self.time_limit = parameters["time_limit"] if ("time_limit" in parameters) else None
        self.decomposition = parameters["decomposition"] if ("decomposition" in parameters) else None
        self.d = parameters["d"] if ("d" in parameters) else None
        self.break_time = parameters["break_time"] if ("break_time" in parameters) else None
        if solution_key_stream is None:
            self.__init_case()
        else:
            self.solution_key_stream = solution_key_stream

    def __init_case(self):
        self.base_cnf = parse_cnf(self.cnf_link)
        init_alg = caser.create_init_case(self.base_cnf, self.crypto_algorithm)

        solver = CaseSolver(self.current_solver)
        solver.start({}, init_alg)
        self.solution_key_stream = init_alg.get_solution_key_stream()
        self.__print_info(init_alg)

    def compute(self, mask, cases=None):
        if cases is None:
            parameters = {
                "key_stream": self.solution_key_stream,
                "secret_mask": mask
            }

            cases = []
            for i in range(self.N):
                parameters["secret_key"] = generator.generate_key(self.crypto_algorithm.secret_key_len)

                case = caser.create_case(self.base_cnf, parameters, self.crypto_algorithm)
                cases.append(case)

        solver_args = {
            "subprocess_thread": self.thread_count,
            "time_limit": self.time_limit,
            "break_time": self.break_time
        }

        m_solver = self.multi_solver(self.current_solver)
        solved_cases, broken_cases = m_solver.start(solver_args, cases)

        times = []
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
            times.append(case.time)

        partially_value = (2 ** np.count_nonzero(mask)) * sum(times)

        if self.decomposition is None:
            time_stat["BROKEN"] = len(broken_cases)

            return partially_value / len(solved_cases), [time_stat, flags_stat]
        else:
            decomposition_values = []

            mf_parameters = {
                "crypto_algorithm": self.crypto_algorithm,
                "cnf_link": self.cnf_link,
                "solver_wrapper": self.current_solver,
                "threads": self.thread_count,
                "time_limit": self.time_limit,
                "decomposition": self.decomposition,
                "break_time": self.break_time,
                "d": self.d
            }

            for case in broken_cases:
                decomposition_value = self.decomposition(mask, case, self.d, GADFunction, mf_parameters)
                decomposition_values.append(decomposition_value)

            time_stat["DETERMINATE"] += len(broken_cases)
            flags_stat["PROCESSING"] += len(broken_cases)

            partially_value += sum(decomposition_values)

            return partially_value / self.N, [time_stat, flags_stat]

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

    def __print_info(self, init_a5):
        print "init key stream: " + format_array(self.solution_key_stream)
        print "init secret key: " + format_array(init_a5.get_solution_secret_key())

        print "init info: (" + init_a5.status + ", " + str(init_a5.time) + ")"
