import threading
import subprocess
import signal
import warnings

from datetime import datetime
from time import sleep, time as now


class Worker(threading.Thread):
    def __init__(self, args):
        self.terminated = threading.Event()
        threading.Thread.__init__(self)
        self.verbosity = args["verbosity"]
        self.tl = args["time_limit"]
        self.solver_wrapper = args["solver_wrapper"]
        self.cases = args["cases"]
        self.locks = args["locks"]
        self.need = True

    def run(self):
        while self.need and not self.terminated.isSet():
            self.locks[0].acquire()
            if len(self.cases[0]) > 0:
                case = self.cases[0].pop()
                self.locks[0].release()
                self.solve(case)
            else:
                self.locks[0].release()
                self.need = False

    def solve(self, case):
        l_args = self.solver_wrapper.get_arguments(tl=self.tl)

        sp = subprocess.Popen(l_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = sp.communicate(str(case.cnf))[0]
        report = self.solver_wrapper.parse_out(output)
        case.mark_solved(report)

        self.locks[1].acquire()
        self.cases[1].append(case)
        self.locks[1].release()


class WorkerSolver:
    def __init__(self, solver_wrapper, sleep_time=1, verbosity=True):
        self.verbosity = verbosity
        self.solver_wrapper = solver_wrapper
        self.last_progress = 0
        self.sleep_time = sleep_time
        self.workers = []

    def __signal_handler(self, s, f):
        print "SIGINT"
        for worker in self.workers:
            worker.terminated.set()
        exit(s)

    def start(self, args, cases):
        self.last_progress = 0
        k = args["subprocess_thread"] if ("subprocess_thread" in args) else 1
        time_limit = args["time_limit"] if ("time_limit" in args) else None

        if "break_time" in args:
            warnings.warn("Break time not support in worker solver", UserWarning)

        solved_cases, broken_cases = [], []
        cases_lock, solved_lock = threading.Lock(), threading.Lock()

        signal.signal(signal.SIGINT, self.__signal_handler)

        worker_args = {
            "verbosity": self.verbosity,
            "time_limit": time_limit,
            "solver_wrapper": self.solver_wrapper,
            "cases": (cases, solved_cases),
            "locks": (cases_lock, solved_lock)
        }

        for i in range(k):
            self.workers.append(Worker(worker_args))

        for worker in self.workers:
            worker.start()

        while self.anyAlive():
            sleep(self.sleep_time)

        times = []
        for s_case in solved_cases:
            times.append(s_case.time)
        if self.verbosity:
            print "progress (" + str(datetime.now()) + ") 100% active(0) with times: " + str(times)

        return solved_cases, broken_cases

    def anyAlive(self):
        return any(worker.isAlive() for worker in self.workers)
