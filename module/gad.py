import subprocess
import threading
import numpy as np

from module.predictive_function import PredictiveFunction, TaskGenerator, InitTaskGenerator
from util import caser, generator, formatter


class GADTaskGenerator(TaskGenerator):
    def __init__(self, args):
        TaskGenerator.__init__(self, args)
        self.init_case = args["init_case"]
        self.mask = args["mask"]

    def get(self, case=None):
        if self.init_case.status is None:
            raise Exception("init case didn't solve")

        parameters = {
            "secret_mask": self.mask,
            "secret_key": generator.generate_key(self.algorithm.secret_key_len),
            "key_stream": self.init_case.get_solution_key_stream(),
        }

        args = self.solver_wrapper.get_arguments()
        case = caser.create_case(self.base_cnf, parameters, self.algorithm)
        return args, case


class GADWorker(threading.Thread):
    def __init__(self, args):
        threading.Thread.__init__(self)
        self.terminated = threading.Event()
        self.task_generator = args["task_generator"]
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
        l_args, case = self.task_generator.get()

        main_sp = subprocess.Popen(l_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = main_sp.communicate(case.get_cnf())[0]
        case.mark_solved(self.task_generator.get_report(output))

        self.locks[1].acquire()
        self.data[1].append((case.get_status(short=True), case.time))
        self.locks[1].release()


class GADFunction(PredictiveFunction):
    def __init__(self, parameters):
        PredictiveFunction.__init__(self, parameters)
        self.decomposition = parameters["decomposition"] if ("decomposition" in parameters) else None

    def solve_init(self):
        init_task_generator = InitTaskGenerator(self.task_generator_args)
        init_args, init_case = init_task_generator.get()

        init_sp = subprocess.Popen(init_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = init_sp.communicate(init_case.get_cnf())[0]
        init_case.mark_solved(init_task_generator.get_report(output))

        return init_case

    def compute(self, mask, cases=()):
        init_case = self.solve_init()
        log = self.__get_info(init_case)

        self.task_generator_args["mask"] = mask
        self.task_generator_args["init_case"] = init_case
        self.worker_args["task_generator"] = GADTaskGenerator(self.task_generator_args)

        solved, time = PredictiveFunction.solve(self, GADWorker, cases)
        time_stat, cases_log = PredictiveFunction.get_time_stat(self, solved)
        log += cases_log
        log += "main phase ended with time: %f\n" % time

        times_sum = 0
        for _, time in solved:
            times_sum += time

        partially_value = (2 ** np.count_nonzero(mask)) * times_sum

        # additional decomposition?
        #

        log += "%s\n" % time_stat
        return partially_value / len(solved), log, solved

    @staticmethod
    def __get_info(case):
        s = "init key stream: %s\n" % formatter.format_array(case.get_solution_key_stream())
        s += "init secret key: %s\n" % formatter.format_array(case.get_solution_secret_key())
        s += "init info: (%s, %f)\n" % (case.get_status(short=True), case.time)
        return s