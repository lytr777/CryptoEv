import signal
import threading
from time import sleep, time as now

from util import caser
from util import parser


class TaskGenerator:
    def __init__(self, args):
        self.base_cnf = args["base_cnf"]
        self.algorithm = args["algorithm"]
        self.solver_wrapper = args["solver_wrapper"]

    def get(self, case):
        raise NotImplementedError

    def get_report(self, output):
        return self.solver_wrapper.parse_out(output)


class InitTaskGenerator(TaskGenerator):
    def __init__(self, args):
        TaskGenerator.__init__(self, args)

    def get(self, case=None):
        init_args = self.solver_wrapper.get_arguments(simplifying=False)
        init_case = caser.create_init_case(self.base_cnf, self.algorithm)

        return init_args, init_case


class PredictiveFunction:
    def __init__(self, parameters):
        self.crypto_algorithm = parameters["crypto_algorithm"]
        self.N = parameters["N"]
        self.solver_wrapper = parameters["solver_wrapper"]

        self.corrector = parameters["corrector"] if ("corrector" in parameters) else None
        self.thread_count = parameters["threads"] if ("threads" in parameters) else 1

        self.base_cnf = parser.parse_cnf(self.crypto_algorithm[1])
        self.sleep_time = 2
        self.task_generator_args = {
            "base_cnf": self.base_cnf,
            "algorithm": self.crypto_algorithm[0],
            "solver_wrapper": self.solver_wrapper
        }
        self.worker_args = {}
        self.workers = []

    def __signal_handler(self, s, f):
        if self.workers is not None:
            for worker in self.workers:
                worker.terminated.set()
        exit(s)

    def compute(self, mask, cases):
        raise NotImplementedError

    def solve(self, worker_constructor, cases):
        signal.signal(signal.SIGINT, self.__signal_handler)

        counter, solved = {"N": self.N}, list(cases)
        self.worker_args["data"] = (counter, solved)
        self.worker_args["locks"] = (threading.Lock(), threading.Lock())

        worker_count = min(self.N, self.thread_count)
        for i in range(worker_count):
            self.workers.append(worker_constructor(self.worker_args))

        for worker in self.workers:
            worker.start()

        start_work_time = now()
        while self.anyAlive():
            sleep(self.sleep_time)

        return solved, now() - start_work_time

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

    def anyAlive(self):
        return any(worker.isAlive() for worker in self.workers)

    @staticmethod
    def __update_time_statistic(time_stat, status):
        if status == "UNSAT" or status == "SAT":
            time_stat["DETERMINATE"] += 1
        else:
            time_stat["INDETERMINATE"] += 1
