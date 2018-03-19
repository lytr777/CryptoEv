import tempfile
import threading
import warnings
import subprocess

from datetime import datetime


class Worker(threading.Thread):
    def __init__(self, args):
        threading.Thread.__init__(self)
        self.verbosity = args["verbosity"]
        self.tl = args["time_limit"]
        self.files = args["files"]
        self.solver_wrapper = args["solver_wrapper"]
        self.cases = args["cases"]
        self.locks = args["locks"]
        self.need = True

    def run(self):
        while self.need:
            self.locks[0].acquire()
            if len(self.cases[0]) > 0:
                case = self.cases[0].pop()
                self.locks[0].release()
                self.solve(case)

                self.locks[1].acquire()
                self.cases[1].append(case)
                self.locks[1].release()
            else:
                self.locks[0].release()
                self.need = False

    def solve(self, case):
        l_args = self.solver_wrapper.get_arguments(self.files[0], self.files[1], tl=self.tl)
        case.write_to(self.files[0])
        sp = subprocess.Popen(l_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = sp.communicate()[0]

        report = self.solver_wrapper.parse_out(self.files[1], output)
        case.mark_solved(report)


class WorkerSolver:
    def __init__(self, solver_wrapper, verbosity=True):
        self.verbosity = verbosity
        self.solver_wrapper = solver_wrapper
        self.last_progress = 0

    def start(self, args, cases):
        self.last_progress = 0
        k = args["subprocess_thread"] if ("subprocess_thread" in args) else 1
        time_limit = args["time_limit"] if ("time_limit" in args) else None
        if "break_time" in args:
            warnings.warn("Break time not support in worker solver", UserWarning)

        solved_cases = []
        cases_lock = threading.Lock()
        solved_lock = threading.Lock()

        workers = []
        for i in range(k):
            cnf_file = tempfile.NamedTemporaryFile(prefix="cnf", suffix=str(i)).name
            out_file = tempfile.NamedTemporaryFile(prefix="out", suffix=str(i)).name
            worker_args = {
                "verbosity": self.verbosity,
                "time_limit": time_limit,
                "files": (cnf_file, out_file),
                "solver_wrapper": self.solver_wrapper,
                "cases": (cases, solved_cases),
                "locks": (cases_lock, solved_lock)
            }
            workers.append(Worker(worker_args))

        for worker in workers:
            worker.start()

        for worker in workers:
            worker.join()

        times = []
        for s_case in solved_cases:
            times.append(s_case.time)
        if self.verbosity:
            print "progress (" + str(datetime.now()) + ") 100% active(0) with times: " + str(times)

        return solved_cases, []
