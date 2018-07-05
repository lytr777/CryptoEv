import subprocess
import threading
import numpy as np

from predictive_function import PredictiveFunction, TaskGenerator, InitTaskGenerator
from util import caser


class IBSTaskGenerator(TaskGenerator):
    def __init__(self, args):
        TaskGenerator.__init__(self, args)
        self.tl = args["time_limit"]
        self.mask = args["mask"]

    def get(self, init_case):
        if init_case.status is None:
            raise Exception("init case didn't solve")

        parameters = {
            "secret_mask": self.mask,
            "secret_key": init_case.get_solution_secret_key(),
            "key_stream": init_case.get_solution_key_stream()
        }

        args = self.solver_wrapper.get_arguments(tl=self.tl)
        case = caser.create_case(self.base_cnf, parameters, self.algorithm)
        return args, case


class IBSWorker(threading.Thread):
    def __init__(self, args):
        threading.Thread.__init__(self)
        self.terminated = threading.Event()
        self.init_task_generator = args["init_task_generator"]
        self.main_task_generator = args["main_task_generator"]
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
        init_args, init_case = self.init_task_generator.get()

        init_sp = subprocess.Popen(init_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = init_sp.communicate(init_case.get_cnf())[0]
        init_case.mark_solved(self.init_task_generator.get_report(output))

        # main
        main_args, case = self.main_task_generator.get(init_case)

        main_sp = subprocess.Popen(main_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = main_sp.communicate(case.get_cnf())[0]
        case.mark_solved(self.main_task_generator.get_report(output))

        self.locks[1].acquire()
        self.data[1].append((case.get_status(short=True), case.time))
        self.locks[1].release()


class IBSFunction(PredictiveFunction):
    def __init__(self, parameters):
        PredictiveFunction.__init__(self, parameters)
        self.time_limit = parameters["time_limit"]

    def compute(self, mask, cases=()):
        self.task_generator_args["time_limit"] = self.time_limit
        self.task_generator_args["mask"] = mask
        self.worker_args["init_task_generator"] = InitTaskGenerator(self.task_generator_args)
        self.worker_args["main_task_generator"] = IBSTaskGenerator(self.task_generator_args)

        solved, time = PredictiveFunction.solve(self, IBSWorker, cases)
        time_stat, log = PredictiveFunction.get_time_stat(self, solved)

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
            value = (2 ** self.crypto_algorithm[0].secret_key_len) * self.time_limit

        log += "%s\n" % time_stat
        return value, log, solved
