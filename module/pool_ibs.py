import signal
import subprocess
import numpy as np
from multiprocessing import Pool
from time import time as now

from model.solver_report import SolverReport
from predictive_function import TaskGenerator


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

    def get_init(self):
        init_args = self.solver_wrapper.get_arguments(self.worker_count, simplifying=False)
        init_case = self.cg.generate_init()

        return init_args, init_case

    def get(self, init_case):
        args = self.solver_wrapper.get_arguments(self.worker_count, tl=self.tl)
        case = self.cg.generate(init_case.solution)

        return args, case


class PoolIBSFunction:
    type = "ibs"

    def __init__(self, parameters):
        self.N = parameters["N"]
        self.time_limit = parameters["time_limit"]
        self.thread_count = parameters["thread_count"]

        self.corrector = parameters["corrector"] if ("corrector" in parameters) else None
        self.debugger = parameters["debugger"] if ("debugger" in parameters) else None
        self.mpi_call = parameters["mpi_call"] if ("mpi_call" in parameters) else False

        self.task_generator_args = {
            "solver_wrapper": parameters["solver_wrapper"],
            "time_limit": self.time_limit,
            "worker_count": parameters["worker_count"] if ("worker_count" in parameters) else 1
        }
        self.pool = None

    def __signal_handler(self, s, f):
        if self.pool is not None:
            self.pool.terminate()
            exit(s)

    def compute(self, cg, cases=()):
        self.debugger.write(1, 0, "init signal handler")
        signal.signal(signal.SIGINT, self.__signal_handler)

        cases = list(cases)
        self.debugger.deferred_write(1, 0, "compute for backdoor: %s" % cg.backdoor)
        self.debugger.deferred_write(1, 0, "set time limit: %s" % self.time_limit)

        self.task_generator_args["case_generator"] = cg
        self.debugger.write(1, 0, "creating task generators")
        task_generator = PoolIBSTaskGenerator(self.task_generator_args)
        tread_count = min(self.N, self.thread_count)
        self.debugger.write(1, 0, "init pool with %d threads" % tread_count)
        self.pool = Pool(processes=tread_count)
        start_work_time = now()

        self.debugger.write(1, 0, "solving...")
        result = self.pool.map_async(solve, [task_generator] * self.N)
        self.pool.close()
        self.pool.join()
        solved, time = result.get(), now() - start_work_time
        cases.extend(solved)
        self.debugger.deferred_write(1, 0, "has been solved %d cases" % len(solved))
        self.debugger.write(1, 0, "spent time: %f" % time)

        if self.mpi_call:
            return None, "", np.array(cases)

        return self.handle_cases(cg, cases, time)

    def handle_cases(self, cg, cases, time):
        self.debugger.write(1, 0, "counting time stat...")
        time_stat, log = self.get_time_stat(cases)
        self.debugger.deferred_write(1, 0, "time stat: %s" % time_stat)

        if self.corrector is not None:
            self.debugger.write(1, 0, "correcting time limit...")
            self.time_limit, dis_count = self.corrector(cases, self.time_limit)
            log += "corrected time limit: %f\n" % self.time_limit
            self.debugger.deferred_write(1, 0, "new time limit: %f" % self.time_limit)

            self.debugger.write(1, 0, "correcting time stat...")
            time_stat["DISCARDED"] = dis_count
            time_stat["DETERMINATE"] -= dis_count
            self.debugger.deferred_write(1, 0, "new time stat: %s" % time_stat)

        log += "spent time: %f\n" % time
        self.debugger.write(1, 0, "calculating value...")
        xi = float(time_stat["DETERMINATE"]) / float(len(cases))
        if xi != 0:
            value = (2 ** len(cg.backdoor)) * self.time_limit * (3 / xi)
        else:
            value = (2 ** cg.algorithm.secret_key_len) * self.time_limit
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
