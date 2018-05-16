import subprocess
import threading

import numpy as np
import signal

from util import caser
from util.parser import parse_cnf
from time import sleep, time as now


class Worker(threading.Thread):
    def __init__(self, args):
        self.terminated = threading.Event()
        threading.Thread.__init__(self)
        self.case_generator = args["case_generator"]
        self.tl = args["time_limit"]
        self.solver_wrapper = args["solver_wrapper"]
        self.data = args["data"]
        self.locks = args["locks"]
        self.need = True

    def run(self):
        while self.need and not self.terminated.isSet():
            self.locks[0].acquire()
            if self.data[0]["N"] > 0:
                self.data[0]["N"] -= 1
                self.locks[0].release()
                self.solve()
            else:
                self.locks[0].release()
                self.need = False

    def solve(self):
        # init
        self.solver_wrapper.set_simplifying(False)
        init_args = self.solver_wrapper.get_arguments(simplifying=False)

        init_case = self.case_generator.get_init()
        init_sp = subprocess.Popen(init_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = init_sp.communicate(init_case.get_cnf())[0]
        report = self.solver_wrapper.parse_out(output)
        init_case.mark_solved(report)

        # main
        self.solver_wrapper.set_simplifying(True)
        l_args = self.solver_wrapper.get_arguments(tl=self.tl)

        case = self.case_generator.get(init_case.get_solution_secret_key(), init_case.get_solution_key_stream())
        init_sp = subprocess.Popen(l_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = init_sp.communicate(case.get_cnf())[0]
        report = self.solver_wrapper.parse_out(output)
        case.mark_solved(report)

        self.locks[1].acquire()
        self.data[1].append((case.get_status(True), case.time))
        self.locks[1].release()


class CaseGenerator:
    def __init__(self, base_cnf, alg, mask):
        self.mask = mask
        self.base_cnf = base_cnf
        self.alg = alg

    def get_init(self):
        return caser.create_init_case(self.base_cnf, self.alg)

    def get(self, secret_key, key_stream):
        parameters = {
            "secret_mask": self.mask,
            "secret_key": secret_key,
            "key_stream": key_stream
        }

        return caser.create_case(self.base_cnf, parameters, self.alg)


class SimpleIBS:
    def __init__(self, parameters):
        self.crypto_algorithm = parameters["crypto_algorithm"]
        self.N = parameters["N"]
        self.current_solver = parameters["solver_wrapper"]
        self.time_limit = parameters["time_limit"]
        self.corrector = parameters["corrector"] if ("corrector" in parameters) else None
        self.log_file = parameters["log_file"] if ("log_file" in parameters) else None
        self.thread_count = parameters["threads"] if ("threads" in parameters) else 1

        self.base_cnf = parse_cnf(self.crypto_algorithm[1])
        self.log = ""
        self.sleep_time = 2
        self.workers = []

    def __signal_handler(self, s, f):
        print "SIGINT"
        for worker in self.workers:
            worker.terminated.set()
        exit(s)

    def compute(self, mask):
        case_generator = CaseGenerator(self.base_cnf, self.crypto_algorithm[0], mask)

        count, solved = {"N": self.N}, []
        count_lock, solved_lock = threading.Lock(), threading.Lock()

        signal.signal(signal.SIGINT, self.__signal_handler)

        worker_args = {
            "case_generator": case_generator,
            "time_limit": self.time_limit,
            "solver_wrapper": self.current_solver,
            "data": (count, solved),
            "locks": (count_lock, solved_lock)
        }

        for i in range(self.thread_count):
            self.workers.append(Worker(worker_args))

        for worker in self.workers:
            worker.start()

        time_stat = {
            "DETERMINATE": 0,
            "INDETERMINATE": 0
        }

        main_start_time = now()

        if self.log_file is not None:
            open(self.log_file, "a").write("times:\n")
        else:
            self.log += "times:\n"

        while self.anyAlive():
            sleep(self.sleep_time)

            if self.log_file is not None:
                log = ""
                solved_lock.acquire()
                while len(solved) > 0:
                    info = solved.pop()
                    log += "%s %f\n" % info
                    self.__update_time_statistic(time_stat, info[0])
                solved_lock.release()
                open(self.log_file, "a").write(log)

        if self.log_file is None:
            for info in solved:
                self.log += "%s %f\n" % info

            if self.corrector is not None:
                self.time_limit = self.corrector(solved, self.time_limit)
                self.log += "time limit has been corrected: %f\n" % self.time_limit
                time_stat["DISCARDED"] = 0

            for info in solved:
                self.__update_time_statistic(time_stat, info[0])

        self.log += "main phase ended with time: %f\n" % (now() - main_start_time)

        xi = float(time_stat["DETERMINATE"]) / float(self.N)
        if xi != 0:
            value = (2 ** np.count_nonzero(mask)) * self.time_limit * (3 / xi)
        else:
            value = (2 ** self.crypto_algorithm[0].secret_key_len) * self.time_limit

        self.log += "%s\n" % time_stat
        re = time_stat["DETERMINATE"] == 1
        return value, self.log, re

    def anyAlive(self):
        return any(worker.isAlive() for worker in self.workers)

    @staticmethod
    def __update_time_statistic(time_stat, status):
        if status == "UNSAT" or status == "SAT":
            time_stat["DETERMINATE"] += 1
        elif status == "DIS":
            time_stat["DISCARDED"] += 1
        else:
            time_stat["INDETERMINATE"] += 1
