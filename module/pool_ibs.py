import subprocess
import numpy as np
from multiprocessing import Pool
from time import time as now

from model.solver_report import SolverReport
from predictive_function import TaskGenerator
from util import caser


def solve(task_generator):
    # init
    init_args, init_case = task_generator.get_init()

    init_sp = subprocess.Popen(init_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = init_sp.communicate(init_case.get_cnf())
    if len(err) != 0 and not err.startswith("timelimit"):
        raise Exception(err)

    report = task_generator.get_report(output)
    init_case.mark_solved(report)

    # main
    main_args, main_case = task_generator.get(init_case)

    main_sp = subprocess.Popen(main_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = main_sp.communicate(main_case.get_cnf())
    if len(err) != 0 and not err.startswith("timelimit"):
        raise Exception(err)

    try:
        report = task_generator.get_report(output)
    except KeyError:
        report = SolverReport("INDETERMINATE", 5.)
    main_case.mark_solved(report)

    return main_case.get_status(short=True), main_case.time


class PoolIBSTaskGenerator(TaskGenerator):
    def __init__(self, args):
        TaskGenerator.__init__(self, args)
        self.tl = args["time_limit"]
        self.mask = args["mask"]

    def get_init(self):
        init_args = self.solver_wrapper.get_arguments(simplifying=False)
        init_case = caser.create_init_case(self.base_cnf, self.algorithm)

        return init_args, init_case

    def get(self, init_case):
        if init_case.status is None or init_case.status != "SATISFIABLE":
            raise Exception("init case not solved")

        parameters = {
            "secret_mask": self.mask,
            "secret_key": init_case.get_solution_secret_key(),
            "key_stream": init_case.get_solution_key_stream()
        }

        args = self.solver_wrapper.get_arguments(tl=self.tl)
        case = caser.create_case(self.base_cnf, parameters, self.algorithm)
        return args, case


class PoolIBSFunction:
    def __init__(self, parameters):
        self.algorithm = parameters["crypto_algorithm"][0]
        self.base_cnf = parameters["crypto_algorithm"][1]
        self.N = parameters["N"]
        self.solver_wrapper = parameters["solver_wrapper"]

        self.corrector = parameters["corrector"] if ("corrector" in parameters) else None
        self.thread_count = parameters["threads"] if ("threads" in parameters) else 1

        self.time_limit = parameters["time_limit"]

    def compute(self, mask, cases=()):
        task_generator_args = {
            "base_cnf": self.base_cnf,
            "algorithm": self.algorithm,
            "solver_wrapper": self.solver_wrapper,
            "mask": mask,
            "time_limit": self.time_limit
        }

        task_generator = PoolIBSTaskGenerator(task_generator_args)
        tread_count = min(self.N, self.thread_count)
        pool = Pool(processes=tread_count)
        start_work_time = now()

        solved = pool.map(solve, [task_generator] * self.N)
        solved.extend(cases)
        time = now() - start_work_time
        time_stat, log = self.get_time_stat(solved)

        if self.corrector is not None:
            self.time_limit, dis_count = self.corrector(solved, self.time_limit)
            log += "time limit has been corrected: %f\n" % self.time_limit

            time_stat["DISCARDED"] = dis_count
            time_stat["DETERMINATE"] -= dis_count

        log += "main phase ended with time: %f\n" % time
        xi = float(time_stat["DETERMINATE"]) / float(len(solved))
        if xi != 0:
            value = (2 ** np.count_nonzero(mask)) * self.time_limit * (3 / xi)
        else:
            value = (2 ** self.algorithm.secret_key_len) * self.time_limit

        log += "%s\n" % time_stat
        return value, log, solved

    def get_time_stat(self, cases):
        time_stat = {
            "DETERMINATE": 0,
            "INDETERMINATE": 0
        }
        cases_log = "times:\n"
        for info in cases:
            cases_log += "%s %f\n" % info
            self.__update_time_statistic(time_stat, info[0])

        return time_stat, cases_log

    @staticmethod
    def __update_time_statistic(time_stat, status):
        if status == "UNSAT" or status == "SAT":
            time_stat["DETERMINATE"] += 1
        else:
            time_stat["INDETERMINATE"] += 1
