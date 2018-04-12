import numpy as np

from solvers.case_solver import CaseSolver
from util import caser, generator
from util.formatter import format_array
from util.parser import parse_cnf


class GADFunction:
    def __init__(self, parameters, solution_key_stream=None):
        self.crypto_algorithm = parameters["crypto_algorithm"]
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
            self.log = ""

    def __init_case(self):
        self.base_cnf = parse_cnf(self.crypto_algorithm[1])
        init_alg = caser.create_init_case(self.base_cnf, self.crypto_algorithm[0])

        solver = CaseSolver(self.current_solver)
        solver.start({}, init_alg)
        self.solution_key_stream = init_alg.get_solution_key_stream()
        self.log = self.__get_info(init_alg)

    def compute(self, mask, cases=None):
        if cases is None:
            decomposition_flag = False
            parameters = {
                "key_stream": self.solution_key_stream,
                "secret_mask": mask
            }

            cases = []
            for i in range(self.N):
                parameters["secret_key"] = generator.generate_key(self.crypto_algorithm[0].secret_key_len)

                case = caser.create_case(self.base_cnf, parameters, self.crypto_algorithm[0])
                cases.append(case)
        else:
            decomposition_flag = True

        solver_args = {
            "subprocess_thread": self.thread_count,
            "time_limit": self.time_limit,
            "break_time": self.break_time
        }

        m_solver = self.multi_solver(self.current_solver)
        solved_cases, broken_cases, solver_log = m_solver.start(solver_args, cases)
        self.log += solver_log

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
                "multi_solver": self.multi_solver,
                "solver_wrapper": self.current_solver,
                "threads": self.thread_count,
                "time_limit": self.time_limit,
                "decomposition": self.decomposition,
                "d": self.d,
                "break_time": self.break_time
            }

            for case in broken_cases:
                decomposition_value, decomposition_log = self.decomposition(mask, case, self.d, GADFunction, mf_parameters)
                decomposition_values.append(decomposition_value)
                self.log += decomposition_log

            time_stat["DETERMINATE"] += len(broken_cases)
            flags_stat["PROCESSING"] += len(broken_cases)

            partially_value += sum(decomposition_values)

            if not decomposition_flag:
                self.log += "%s\n" % time_stat
                self.log += "%s\n" % flags_stat
            return partially_value / self.N, self.log

    @staticmethod
    def __update_time_statistic(time_stat, status):
        if status == "UNSATISFIABLE" or status == "SATISFIABLE":
            time_stat["DETERMINATE"] += 1
        else:
            time_stat["INDETERMINATE"] += 1

    @staticmethod
    def __update_flags_statistic(flags_stat, flags):
        if flags[0]:
            flags_stat["PREPROCESSING"] += 1
        else:
            flags_stat["PROCESSING"] += 1

    def __get_info(self, init_a5):
        s = "init key stream: %s\n" % format_array(self.solution_key_stream)
        s += "init secret key: %s\n" % format_array(init_a5.get_solution_secret_key())
        s += "init info: (%s, %f)\n" % (init_a5.status, init_a5.time)
        return s

