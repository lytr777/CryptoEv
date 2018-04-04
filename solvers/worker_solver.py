import tempfile
import threading
import subprocess
import os
import signal

from datetime import datetime
from time import sleep, time as now


class Worker(threading.Thread):
    sleep_time = [0.05, 0.05, 0.1, 0.2, 0.3, 0.5, 1]

    def __init__(self, args):
        self.terminated = threading.Event()
        threading.Thread.__init__(self)
        self.verbosity = args["verbosity"]
        self.tl = args["time_limit"]
        self.break_time = args["break_time"]
        self.files = args["files"]
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
        l_args = self.solver_wrapper.get_arguments(self.files[0], self.files[1], tl=self.tl)
        case.write_to(self.files[0])

        start_time = now()
        sleep_i = 0
        broken = False
        sp = subprocess.Popen(l_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        while sp.poll() is None:
            if self.terminated.isSet():
                return

            if (self.break_time is not None) and (self.break_time <= now() - start_time):
                sp.terminate()
                sp.wait()
                broken = True
                break

            sleep(self.sleep_time[min(sleep_i, len(self.sleep_time) - 1)])
            sleep_i += 1

        output = sp.communicate()[0]
        report = self.solver_wrapper.parse_out(self.files[1], output)
        case.mark_solved(report)

        if broken:
            self.locks[2].acquire()
            self.cases[2].append(case)
            self.locks[2].release()
        else:
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
        break_time = args["break_time"] if ("break_time" in args) else None

        solved_cases, broken_cases = [], []
        cases_lock = threading.Lock()
        solved_lock = threading.Lock()
        broken_lock = threading.Lock()

        signal.signal(signal.SIGINT, self.__signal_handler)

        for i in range(k):
            cnf_file = tempfile.NamedTemporaryFile(prefix="cnf", suffix=str(i)).name
            out_file = tempfile.NamedTemporaryFile(prefix="out", suffix=str(i)).name
            worker_args = {
                "verbosity": self.verbosity,
                "time_limit": time_limit,
                "break_time": break_time,
                "files": (cnf_file, out_file),
                "solver_wrapper": self.solver_wrapper,
                "cases": (cases, solved_cases, broken_cases),
                "locks": (cases_lock, solved_lock, broken_lock)
            }
            self.workers.append(Worker(worker_args))

        for worker in self.workers:
            worker.start()

        while self.anyAlive():
            sleep(self.sleep_time)

        for worker in self.workers:
            if os.path.isfile(worker.files[0]):
                os.remove(worker.files[0])
            if os.path.isfile(worker.files[1]):
                os.remove(worker.files[1])

        times = []
        for s_case in solved_cases:
            times.append(s_case.time)
        if self.verbosity:
            print "progress (" + str(datetime.now()) + ") 100% active(0) with times: " + str(times)

        return solved_cases, broken_cases

    def anyAlive(self):
        return any(worker.isAlive() for worker in self.workers)
