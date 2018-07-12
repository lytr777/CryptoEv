import subprocess
import threading
import numpy as np

from predictive_function import PredictiveFunction, TaskGenerator, InitTaskGenerator
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

        args = self.solver_wrapper.get_timelimit_arguments(tl=self.tl)
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

        while init_case.status != "SATISFIABLE":
            self.debugger.write(3, 2, "%s start solving init case with secret key: %s" % (
                threading.Thread.getName(self),
                formatter.format_array(init_case.secret_key)
            ))
            init_sp = subprocess.Popen(init_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, err = init_sp.communicate(init_case.get_cnf())
            if len(err) != 0 and not err.startswith("timelimit"):
                self.debugger.write(3, 2, "%s didn't solve init case:\n%s" % (threading.Thread.getName(self), err))
                raise Exception(err)

            report = self.init_task_generator.get_report(output)
            self.debugger.write(3, 2, "%s solved init case with status: %s" % (
                threading.Thread.getName(self),
                report.status
            ))
            init_case.mark_solved(report)

        # main
        self.debugger.write(3, 2, "%s generate main case" % (threading.Thread.getName(self)))
        main_args, main_case = self.main_task_generator.get(init_case)

        self.debugger.write(3, 2, "%s get main args: %s" % (threading.Thread.getName(self), main_args))
        self.debugger.write(3, 2, "%s start solving main case with secret key: %s" % (
            threading.Thread.getName(self), formatter.format_array(main_case.secret_key, main_case.secret_mask)
        ))
        main_sp = subprocess.Popen(main_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = main_sp.communicate(main_case.get_cnf())
        if len(err) != 0 and not err.startswith("timelimit"):
            self.debugger.write(3, 2, "%s didn't solve main case:\n%s" % (threading.Thread.getName(self), err))
            raise Exception(err)

        report = self.main_task_generator.get_report(output)
        self.debugger.write(3, 2, "%s solved main case with status: %s and time: %f" % (
            threading.Thread.getName(self),
            report.status,
            report.time
        ))
        main_case.mark_solved(report)

        self.locks[1].acquire()
        self.data[1].append((main_case.get_status(short=True), main_case.time))
        self.locks[1].release()


class IBSFunction(PredictiveFunction):
    def __init__(self, parameters):
        PredictiveFunction.__init__(self, parameters)
        self.time_limit = parameters["time_limit"]

    def compute(self, mask, cases=()):
        self.task_generator_args["mask"] = mask
        self.debugger.deferred_write(1, 0, "compute for mask: %s" % formatter.format_array(mask))
        self.task_generator_args["time_limit"] = self.time_limit
        self.debugger.deferred_write(1, 0, "set time limit: %s" % self.time_limit)

        self.debugger.deferred_write(1, 0, "creating task generators")
        self.worker_args["init_task_generator"] = InitTaskGenerator(self.task_generator_args)
        self.worker_args["main_task_generator"] = IBSTaskGenerator(self.task_generator_args)

        self.debugger.write(1, 0, "solving...")
        solved, time = PredictiveFunction.solve(self, IBSWorker, cases)
        self.debugger.write(1, 0, "has been solved")
        self.debugger.deferred_write(1, 0, "counting time stat...")
        time_stat, log = PredictiveFunction.get_time_stat(self, solved)
        self.debugger.deferred_write(1, 0, "time stat: %s" % time_stat)

        if self.corrector is not None:
            self.debugger.deferred_write(1, 0, "correcting time limit...")
            self.time_limit, dis_count = self.corrector(solved, self.time_limit)
            log += "time limit has been corrected: %f\n" % self.time_limit
            self.debugger.deferred_write(1, 0, "new time limit: %f" % self.time_limit)

            self.debugger.deferred_write(1, 0, "correcting time stat...")
            time_stat["DISCARDED"] = dis_count
            time_stat["DETERMINATE"] -= dis_count
            self.debugger.deferred_write(1, 0, "new time stat: %s" % time_stat)

        log += "main phase ended with time: %f\n" % time
        self.debugger.deferred_write(1, 0, "calculating value...")
        xi = float(time_stat["DETERMINATE"]) / float(len(solved))
        if xi != 0:
            value = (2 ** np.count_nonzero(mask)) * self.time_limit * (3 / xi)
        else:
            value = (2 ** self.algorithm.secret_key_len) * self.time_limit
        self.debugger.deferred_write(1, 0, "value: %.7g\n" % value)

        log += "%s\n" % time_stat
        return value, log, solved
