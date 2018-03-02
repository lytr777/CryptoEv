import subprocess
import tempfile
import os
import numpy as np
from time import sleep, time as now
from datetime import datetime


class MultiCaseSolver:
    def __init__(self, solver_wrapper, sleep_time=2):
        self.solver_wrapper = solver_wrapper
        self.sleep_time = sleep_time
        self.last_progress = 0

    def start(self, args, cases):
        self.last_progress = 0
        k = args["subprocess_thread"] if ("subprocess_thread" in args) else 1
        time_limit = args["time_limit"] if ("time_limit" in args) else None
        break_time = args["break_time"] if ("break_time" in args) else None

        cnf_files = []
        out_files = []
        launching_args = []
        for i in range(k):
            cnf_files.append(tempfile.NamedTemporaryFile(prefix="cnf", suffix=str(i)).name)
            out_files.append(tempfile.NamedTemporaryFile(prefix="out", suffix=str(i)).name)

            launching_args.append(self.solver_wrapper.get_arguments(cnf_files[i], out_files[i], time_limit=time_limit))

        free = range(k)
        subprocesses = []
        subprocess_times = np.zeros(k, dtype=np.int)
        solved_cases = []
        broke_cases = []

        break_f = lambda x: (break_time is not None) and (now() - subprocess_times[x] > break_time)
        while len(cases) > 0:
            while len(subprocesses) < k:
                free_index = free.pop()

                case = cases.pop()
                l_args = launching_args[free_index]
                case.write_to(cnf_files[free_index])

                new_sp = subprocess.Popen(l_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                subprocesses.append((free_index, new_sp, case))
                subprocess_times[free_index] = now()

                if len(cases) == 0:
                    break

            self.check_subprocesses(free, out_files, cases, solved_cases, broke_cases, subprocesses, break_f)

        while len(subprocesses) > 0:
            self.check_subprocesses(free, out_files, cases, solved_cases, broke_cases, subprocesses, break_f)

        for i in range(k):
            if os.path.isfile(cnf_files[i]):
                os.remove(cnf_files[i])
            if os.path.isfile(out_files[i]):
                os.remove(out_files[i])

        return solved_cases, broke_cases

    def check_subprocesses(self, free, out_files, cases, solved_cases, broke_cases, subprocesses, break_f):
        sleep(self.sleep_time)
        j = 0
        times = []
        while j < len(subprocesses):
            sp = subprocesses[j][1]
            i = subprocesses[j][0]
            if sp.poll() is not None:
                case = subprocesses[j][2]
                self.__handle_sp(sp, out_files[i], case)

                subprocesses.pop(j)
                solved_cases.append(case)
                free.append(i)

                times.append(case.time)
                # print "subprocess " + str(i) + " ended with result (" + case.status + ", " + str(case.time) + ")"
            else:
                if break_f(i):
                    case = subprocesses[j][2]
                    sp.terminate()
                    sp.wait()

                    subprocesses.pop(j)
                    broke_cases.append(case)
                    free.append(i)
                else:
                    j += 1

        self.__print_progress(len(solved_cases), len(broke_cases), len(cases), len(subprocesses), times)

    def __handle_sp(self, sp, out_file, case):
        output = sp.communicate()[0]
        report = self.solver_wrapper.parse_out(out_file, output)

        case.mark_solved(report)

    def __print_progress(self, solved, broke, waiting, solving, times):
        progress = (broke + solved) * 100. / (solved + broke + waiting + solving)
        # if self.last_progress != progress:
        if len(times) != 0:
            print "progress (" + str(datetime.now()) + ") " + str("%.2f" % progress) + "% active(" + str(solving) + ") with times: " + str(times)
            self.last_progress = progress
