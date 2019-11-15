import os
import signal
import subprocess

from time import sleep, time as now
from multiprocessing.pool import Pool
from multiprocessing.process import Process

from constants.runtime import runtime_constants as rc


def task_function(task):
    return task.solve()


class MyProcess(Process):
    def terminate(self):
        spc = subprocess.Popen("pgrep -P %d" % self.pid, shell=True, stdout=subprocess.PIPE)
        ps_out = spc.stdout.read()
        spc.wait()
        for pid in ps_out.strip().split("\n"):
            try:
                os.kill(int(pid), signal.SIGTERM)
            except Exception:
                pass
        super(MyProcess, self).terminate()


class MyPool(Pool):
    Process = MyProcess


class TLApplyPool:
    def __init__(self, **kwargs):
        self.thread_count = kwargs["thread_count"]
        self.pool = MyPool(processes=self.thread_count)

        signal.signal(signal.SIGINT, self.__signal_handler)

    def __signal_handler(self, s, f):
        if self.pool is not None:
            self.pool.terminate()
            exit(s)

    def solve(self, tasks, complexity=1, **kwargs):
        process_count, remainder = divmod(self.thread_count, complexity)

        if process_count == 0 or remainder != 0:
            raise Exception("Incorrect number of threads or workers")
        if process_count != self.thread_count:
            raise Exception("Pool don't support resizing")

        res_list, result = [], []
        start_work_time = now()
        for task in tasks:
            res = self.pool.apply_async(task_function, (task,))
            res_list.append(res)

        tl = float(rc.best[1]) / (2 ** kwargs['s']) * 1.3
        rc.debugger.write(2, 3, "pool tl: %f" % tl)
        left_time, p_time = tl, 0.
        while len(res_list) > 0 and left_time > 0:
            timestamp = now()
            res_list[0].wait(left_time)
            p_time += now() - timestamp

            i = 0
            while i < len(res_list):
                if res_list[i].ready():
                    p_time = 0.
                    res = res_list.pop(i)
                    if res.successful():
                        result.append(res.get())
                    else:
                        rc.debugger.write(0, 1, "Pool solving was completed unsuccessfully")
                        result.append(res.get())
                else:
                    i += 1

            rc.debugger.write(2, 3, "Already solved %d tasks" % len(result))

            p_time_count = min(self.thread_count, len(res_list))
            time_sum = p_time * p_time_count
            for _, time in result:
                time_sum += float(time)

            left_time = tl - (time_sum / len(tasks))

        if len(res_list) > 0:
            rc.debugger.write(2, 3, "Terminate pool (%.2f > %.2f)" % (tl - left_time, tl))

            self.pool.terminate()
            del self.pool
            self.pool = MyPool(processes=self.thread_count)

            left = len(tasks) - len(result)
            result.extend([('INDETERMINATE', float("inf"))] * left)

        return result, now() - start_work_time

    def terminate(self):
        self.pool.terminate()
