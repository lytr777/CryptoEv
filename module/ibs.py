import subprocess
import threading
import numpy as np

from key_generators.block_cipher import BlockCipher
from model.solver_report import SolverReport
from predictive_function import PredictiveFunction, TaskGenerator, InitTaskGenerator, SubprocessHelper
from util import caser, formatter


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
        if isinstance(init_case, BlockCipher):
            parameters["public_key"] = init_case.get_solution_public_key()

        args = self.solver_wrapper.get_arguments(tl=self.tl)
        case = caser.create_case(self.base_cnf, parameters, self.algorithm)
        return args, case


class IBSWorker(threading.Thread):
    def __init__(self, args):
        threading.Thread.__init__(self)
        self.terminated = threading.Event()
        self.init_task_generator = args["init_task_generator"]
        self.main_task_generator = args["main_task_generator"]
        self.debugger = args["debugger"]
        self.data = args["data"]
        self.locks = args["locks"]
        self.need = True
        self.sp_helper = SubprocessHelper(5, self.debugger)

    def run(self):
        while self.need and not self.terminated.isSet():
            self.debugger.write(3, 2, "%s wait lock 0" % threading.Thread.getName(self))
            self.locks[0].acquire()
            if self.data[0]["N"] > 0:
                self.data[0]["N"] -= 1
                left = self.data[0]["N"]
                self.locks[0].release()
                self.debugger.write(3, 2, "%s acquire and release lock 0 and get new case, left: %d" % (
                    threading.Thread.getName(self),
                    left
                ))
                self.solve()
            else:
                self.locks[0].release()
                self.debugger.write(3, 2, "left 0 cases, %s terminating..." % (threading.Thread.getName(self)))
                self.need = False

    def solve(self):
        # init
        self.debugger.write(3, 2, "%s generate init case" % (threading.Thread.getName(self)))
        init_args, init_case = self.init_task_generator.get()

        init_report = self.sp_helper.run({
            "name": "init",
            "args": init_args,
            "case": init_case,
            "output_parser": self.init_task_generator.get_report,
            "thread_name": threading.Thread.getName(self)
        })
        init_case.mark_solved(init_report)

        # main
        self.debugger.write(3, 2, "%s generate main case" % (threading.Thread.getName(self)))
        main_args, main_case = self.main_task_generator.get(init_case)
        self.debugger.deferred_write(3, 2, "%s get main args: %s" % (threading.Thread.getName(self), main_args))

        main_report = self.sp_helper.run({
            "name": "main",
            "args": main_args,
            "case": main_case,
            "output_parser": self.main_task_generator.get_report,
            "thread_name": threading.Thread.getName(self)
        })
        main_case.mark_solved(main_report)

        self.locks[1].acquire()
        self.data[1].append((main_case.get_status(short=True), main_case.time))
        self.locks[1].release()


class IBSFunction(PredictiveFunction):
    def __init__(self, parameters):
        PredictiveFunction.__init__(self, parameters)
        self.time_limit = parameters["time_limit"]
        self.mpi_call = parameters["mpi_call"] if ("mpi_call" in parameters) else False

    def compute(self, mask, cases=()):
        cases = list(cases)
        self.task_generator_args["mask"] = mask
        self.debugger.deferred_write(1, 0, "compute for mask: %s" % formatter.format_array(mask))
        self.task_generator_args["time_limit"] = self.time_limit
        self.debugger.deferred_write(1, 0, "set time limit: %s" % self.time_limit)

        self.debugger.write(1, 0, "creating task generators")
        self.worker_args["init_task_generator"] = InitTaskGenerator(self.task_generator_args)
        self.worker_args["main_task_generator"] = IBSTaskGenerator(self.task_generator_args)

        self.debugger.write(1, 0, "solving...")
        solved, time = PredictiveFunction.solve(self, IBSWorker)
        cases.extend(solved)
        self.debugger.deferred_write(1, 0, "has been solved %d cases" % len(solved))
        self.debugger.write(1, 0, "spent time: %f" % time)

        if self.mpi_call:
            return None, "", np.array(cases)

        return self.handle_cases(mask, cases, time)

    def handle_cases(self, mask, cases, time):
        self.debugger.write(1, 0, "counting time stat...")
        time_stat, log = self.get_time_stat(cases)
        self.debugger.deferred_write(1, 0, "time stat: %s" % time_stat)

        if self.corrector is not None:
            self.debugger.write(1, 0, "correcting time limit...")
            self.time_limit, dis_count = self.corrector(cases, self.time_limit)
            log += "time limit has been corrected: %f\n" % self.time_limit
            self.debugger.deferred_write(1, 0, "new time limit: %f" % self.time_limit)

            self.debugger.write(1, 0, "correcting time stat...")
            time_stat["DISCARDED"] = dis_count
            time_stat["DETERMINATE"] -= dis_count
            self.debugger.deferred_write(1, 0, "new time stat: %s" % time_stat)

        log += "main phase ended with time: %f\n" % time
        self.debugger.write(1, 0, "calculating value...")
        xi = float(time_stat["DETERMINATE"]) / float(len(cases))
        if xi != 0:
            value = (2 ** np.count_nonzero(mask)) * self.time_limit * (3 / xi)
        else:
            value = (2 ** self.algorithm.secret_key_len) * self.time_limit
        self.debugger.write(1, 0, "value: %.7g\n" % value)

        log += "%s\n" % time_stat
        return value, log, cases
