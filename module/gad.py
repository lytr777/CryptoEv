import subprocess
import threading
import numpy as np

from module.predictive_function import PredictiveFunction, TaskGenerator, InitTaskGenerator, SubprocessHelper
from util import formatter


class GADTaskGenerator(TaskGenerator):
    def __init__(self, args):
        TaskGenerator.__init__(self, args)
        self.init_case = args["init_case"]

    def get(self, case=None):
        args = self.solver_wrapper.get_arguments(self.worker_count)
        case = self.cg.generate(self.init_case.solution)

        return args, case


class GADWorker(threading.Thread):
    def __init__(self, args):
        threading.Thread.__init__(self)
        self.terminated = threading.Event()
        self.task_generator = args["task_generator"]
        self.debugger = args["debugger"]
        self.data = args["data"]
        self.locks = args["locks"]
        self.need = True
        self.sp_helper = SubprocessHelper(5, self.debugger)

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

        main_report = self.sp_helper.run({
            "name": "main",
            "args": l_args,
            "case": case,
            "output_parser": self.task_generator.get_report,
            "thread_name": threading.Thread.getName(self)
        })
        case.mark_solved(main_report)

        self.locks[1].acquire()
        self.data[1].append((case.get_status(short=True), case.time))
        self.locks[1].release()


class GADFunction(PredictiveFunction):
    type = "gad"

    def __init__(self, parameters):
        PredictiveFunction.__init__(self, parameters)
        self.decomposition = parameters["decomposition"] if ("decomposition" in parameters) else None

    def solve_init(self):
        init_task_generator = InitTaskGenerator(self.task_generator_args)
        init_args, init_case = init_task_generator.get()

        init_sp = subprocess.Popen(init_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = init_sp.communicate(init_case.get_cnf())[0]
        init_case.mark_solved(init_task_generator.get_report(output))
        init_case.check_solution()

        return init_case

    def compute(self, cg, cases=()):
        init_case = self.solve_init()
        log = self.__get_info(init_case)

        cases = list(cases)
        self.task_generator_args["case_generator"] = cg
        self.task_generator_args["init_case"] = init_case
        self.worker_args["task_generator"] = GADTaskGenerator(self.task_generator_args)

        solved, time = PredictiveFunction.solve(self, GADWorker)
        cases.extend(solved)

        if self.mpi_call:
            return None, "", np.array(cases)

        time_stat, cases_log = PredictiveFunction.get_time_stat(self, cases)
        log += cases_log
        log += "spent time: %f" % time

        times_sum = 0
        for _, time in cases:
            times_sum += time

        partially_value = (2 ** len(cg.backdoor)) * times_sum

        # additional decomposition?
        #

        log += "%s\n" % time_stat
        return partially_value / len(cases), log, cases

    @staticmethod
    def __get_info(case):
        s = "init secret key: %s\n" % formatter.format_array(case.get_solution_secret_key())
        s += "init key stream: %s\n" % formatter.format_array(case.get_solution_key_stream())
        s += "init info: (%s, %f)\n" % (case.get_status(short=True), case.time)
        return s
