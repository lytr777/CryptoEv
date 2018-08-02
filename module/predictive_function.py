import signal
import subprocess
import threading
from time import sleep, time as now

from model.solver_report import SolverReport
from util import caser, formatter


class SubprocessHelper:
    def __init__(self, tries, debugger):
        self.tries = tries
        self.debugger = debugger

    def run(self, parameters):
        name = parameters["name"]
        args = parameters["args"]
        case = parameters["case"]
        output_parser = parameters["output_parser"]
        thread_name = parameters["thread_name"]
        report = None

        for i in range(self.tries):
            if report is None or report.check():
                self.debugger.write(3, 2, "%s start solving %s case with secret key: %s" % (
                    thread_name, name, formatter.format_array(case.secret_key)
                ))
                init_sp = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, err = init_sp.communicate(case.get_cnf())
                if len(err) != 0 and not err.startswith("timelimit"):
                    self.debugger.write(1, 2, "%s didn't solve %s case:\n%s" % (thread_name, name, err))
                    raise Exception(err)

                try:
                    report = output_parser(output)
                except KeyError:
                    self.debugger.write(1, 2, "%s error while parsing %s case" % (thread_name, name))
                    report = SolverReport("INDETERMINATE", 5.)
                self.debugger.write(3, 2, "%s solved %s case with status: %s" % (thread_name, name, report.status))
            else:
                break

        if report.check():
            raise Exception("All %d times main case hasn't been solved" % self.tries)
        return report


class TaskGenerator:
    def __init__(self, args):
        self.base_cnf = args["base_cnf"]
        self.algorithm = args["algorithm"]
        self.solver_wrapper = args["solver_wrapper"]

    def get(self, case):
        raise NotImplementedError

    def get_report(self, output):
        return self.solver_wrapper.parse_out(output, self.algorithm)


class InitTaskGenerator(TaskGenerator):
    def __init__(self, args):
        TaskGenerator.__init__(self, args)

    def get(self, case=None):
        init_args = self.solver_wrapper.get_arguments(simplifying=False)
        init_case = caser.create_init_case(self.base_cnf, self.algorithm)

        return init_args, init_case


class PredictiveFunction:
    def __init__(self, parameters):
        self.algorithm = parameters["crypto_algorithm"][0]
        self.base_cnf = parameters["crypto_algorithm"][1]
        self.N = parameters["N"]
        self.solver_wrapper = parameters["solver_wrapper"]

        self.corrector = parameters["corrector"] if ("corrector" in parameters) else None
        self.thread_count = parameters["threads"] if ("threads" in parameters) else 1
        self.debugger = parameters["debugger"] if ("debugger" in parameters) else None

        self.sleep_time = 2
        self.task_generator_args = {
            "base_cnf": self.base_cnf,
            "algorithm": self.algorithm,
            "solver_wrapper": self.solver_wrapper
        }
        self.worker_args = {"debugger": self.debugger}
        self.workers = []

    def __signal_handler(self, s, f):
        for worker in self.workers:
            worker.terminated.set()
        exit(s)

    def compute(self, mask, cases):
        raise NotImplementedError

    def solve(self, worker_constructor):
        self.debugger.write(1, 1, "init signal handler")
        signal.signal(signal.SIGINT, self.__signal_handler)

        counter, solved = {"N": self.N}, []
        self.worker_args["data"] = (counter, solved)
        self.worker_args["locks"] = (threading.Lock(), threading.Lock())
        self.debugger.deferred_write(1, 1, "defining data %s and locks" % str(self.worker_args["data"]))

        worker_count = min(self.N, self.thread_count)
        self.debugger.write(1, 1, "updating worker count: %d" % worker_count)
        for i in range(worker_count):
            self.workers.append(worker_constructor(self.worker_args))
        self.debugger.deferred_write(1, 1, "create %d workers" % len(self.workers))

        self.debugger.write(1, 1, "starting workers...")
        for worker in self.workers:
            worker.start()
            self.debugger.write(2, 1, "%s started" % worker.getName())
        self.debugger.write(1, 1, "has started %d workers" % len(self.workers))

        start_work_time = now()
        while self.anyAlive():
            sleep(self.sleep_time)
            self.debugger.write(1, 1, "%d of %d cases solved" % (len(solved), self.N))

        return solved, now() - start_work_time

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

    def anyAlive(self):
        self.debugger.deferred_write(1, 1, "checking workers statuses...")
        count = 0
        for worker in self.workers:
            if worker.isAlive():
                count += 1
                self.debugger.deferred_write(2, 1, "%s alive" % worker.getName())
            else:
                self.debugger.deferred_write(2, 1, "%s not alive" % worker.getName())
        self.debugger.write(1, 1, "%d worker(s) is alive" % count)
        return count != 0

    @staticmethod
    def __update_time_statistic(time_stat, status):
        if status == "UNSAT" or status == "SAT":
            time_stat["DETERMINATE"] += 1
        else:
            time_stat["INDETERMINATE"] += 1
