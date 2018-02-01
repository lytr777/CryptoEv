import numpy as np

from module.case_solver import CaseSolver
from module.multi_case_solver import MultiCaseSolver
from util import caser, generator
from util.formatter import format_array
from util.parser import parse_cnf


class PredictiveFunction:
    def __init__(self, parameters, solution_key_stream=None):
        self.crypto_algorithm = parameters["crypto_algorithm"]
        self.cnf_link = parameters["cnf_link"]
        self.N = parameters["N"]
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

        multi_solver = MultiCaseSolver(self.current_solver)
        solved_cases, broke_cases = multi_solver.start(solver_args, cases)

        times = []
        time_stats = {
            "DETERMINATE": 0,
            "INDETERMINATE": 0
        }

        for case in solved_cases:
            self.__update_time_statistic(time_stats, case.status)
            times.append(case.time)

        partially_metric = (2 ** np.count_nonzero(mask)) * sum(times)

        if self.decomposition is None:
            time_stats["BROKE"] = len(broke_cases)

            return partially_metric / len(solved_cases), time_stats
        else:
            decomposition_metrics = []

            pf_parameters = {
                "crypto_algorithm": self.crypto_algorithm,
                "cnf_link": self.cnf_link,
                "solver_wrapper": self.current_solver,
                "threads": self.thread_count,
                "time_limit": self.time_limit,
                "decomposition": self.decomposition,
                "break_time": self.break_time,
                "d": self.d
            }

            for case in broke_cases:
                decomposition_metric = self.decomposition(mask, case, self.d, pf_parameters)
                decomposition_metrics.append(decomposition_metric)

            time_stats["DETERMINATE"] += len(broke_cases)

            partially_metric += sum(decomposition_metrics)

            return partially_metric / self.N, time_stats

    def __update_time_statistic(self, time_stats, status):
        if status == "UNSATISFIABLE" or status == "SATISFIABLE":
            time_stats["DETERMINATE"] += 1
        else:
            time_stats["INDETERMINATE"] += 1

    def __print_info(self, init_a5):
        print "init key stream: " + format_array(self.solution_key_stream)
        print "init secret key: " + format_array(init_a5.get_solution_secret_key())

        print "init info: (" + init_a5.status + ", " + str(init_a5.time) + ")"
