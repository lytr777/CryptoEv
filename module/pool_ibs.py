import subprocess
import numpy as np
from multiprocessing import Pool
from time import time as now

import signal

from model.solver_report import SolverReport
from predictive_function import TaskGenerator
from util import caser, formatter


def solve(task_generator):
    # init
    init_args, init_case = task_generator.get_init()

    init_report = None
    tries = 5
    for i in range(tries):
        if init_report is None or init_report.check():
            init_sp = subprocess.Popen(init_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, err = init_sp.communicate(init_case.get_cnf())
            if len(err) != 0 and not err.startswith("timelimit"):
                raise Exception(err)

            init_report = task_generator.get_report(output)
        else:
            break

    if init_report.check():
        raise Exception("All %d times init case hasn't been solved" % tries)
    init_case.mark_solved(init_report)

    # main
    main_args, main_case = task_generator.get(init_case)

    main_report = None
    tries = 5
    for i in range(tries):
        if main_report is None or main_report.check():
            main_sp = subprocess.Popen(main_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, err = main_sp.communicate(main_case.get_cnf())
            if len(err) != 0 and not err.startswith("timelimit"):
                raise Exception(err)

            try:
                main_report = task_generator.get_report(output)
            except KeyError:
                main_report = SolverReport("INDETERMINATE", 5.)
        else:
            break

    if main_report.check():
        raise Exception("All %d times main case hasn't been solved" % tries)
    main_case.mark_solved(main_report)

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
        self.debugger = parameters["debugger"] if ("debugger" in parameters) else None
        self.mpi_call = parameters["mpi_call"] if ("mpi_call" in parameters) else False

        self.time_limit = parameters["time_limit"]
        self.pool = None

    def __signal_handler(self, s, f):
        if self.pool is not None:
            self.pool.terminate()
            exit(s)

    def compute(self, mask, cases=()):
        self.debugger.write(1, 1, "init signal handler")
        signal.signal(signal.SIGINT, self.__signal_handler)

        task_generator_args = {
            "base_cnf": self.base_cnf,
            "algorithm": self.algorithm,
            "solver_wrapper": self.solver_wrapper,
            "mask": mask,
            "time_limit": self.time_limit
        }
        cases = list(cases)
        self.debugger.deferred_write(1, 0, "compute for mask: %s" % formatter.format_array(mask))
        self.debugger.deferred_write(1, 0, "set time limit: %s" % self.time_limit)

        self.debugger.write(1, 0, "creating task generators")
        task_generator = PoolIBSTaskGenerator(task_generator_args)
        tread_count = min(self.N, self.thread_count)
        self.debugger.write(1, 0, "init pool with %d threads" % tread_count)
        self.pool = Pool(processes=tread_count)
        start_work_time = now()

        self.debugger.write(1, 0, "solving...")
        result = self.pool.map_async(solve, [task_generator] * self.N)
        self.pool.close()
        self.pool.join()
        cases.extend(result.get())
        self.debugger.deferred_write(1, 0, "has been solved")

        if self.mpi_call:
            return None, "", np.array(cases)

        time = now() - start_work_time

        return self.handle_cases(mask, cases, time)

    def handle_cases(self, mask, cases, time):
        self.debugger.write(1, 0, "counting time stat...")
        time_stat, log = self.get_time_stat(cases)
        self.debugger.deferred_write(1, 0, "time stat: %s" % time_stat)

        if self.corrector is not None:
            self.debugger.write(1, 0, "correcting time limit...")
            self.time_limit, dis_count = self.corrector(cases, self.time_limit)
            log += "time limit has been corrected: %f\n" % self.time_limit
            self.debugger.deferred_write(1, 0, "new time limit: %f" % self.time_limit)

            self.debugger.write(1, 0, "correcting time stat...")
            time_stat["DISCARDED"] = dis_count
            time_stat["DETERMINATE"] -= dis_count
            self.debugger.deferred_write(1, 0, "new time stat: %s" % time_stat)

        log += "main phase ended with time: %f\n" % time
        self.debugger.write(1, 0, "calculating value...")
        xi = float(time_stat["DETERMINATE"]) / float(len(cases))
        if xi != 0:
            value = (2 ** np.count_nonzero(mask)) * self.time_limit * (3 / xi)
        else:
            value = (2 ** self.algorithm.secret_key_len) * self.time_limit
        self.debugger.write(1, 0, "value: %.7g\n" % value)

        log += "%s\n" % time_stat
        return value, log, cases

    def get_time_stat(self, cases):
        time_stat = {
            "DETERMINATE": 0,
            "INDETERMINATE": 0
        }
        cases_log = "times:\n"
        for info in cases:
            cases_log += "%s %s\n" % (info[0], info[1])
            self.__update_time_statistic(time_stat, info[0])

        return time_stat, cases_log

    @staticmethod
    def __update_time_statistic(time_stat, status):
        if status == "UNSAT" or status == "SAT":
            time_stat["DETERMINATE"] += 1
        else:
            time_stat["INDETERMINATE"] += 1
