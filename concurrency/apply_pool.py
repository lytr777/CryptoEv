import signal

from time import sleep, time as now
from multiprocessing import Pool
from constants.runtime import runtime_constants as rc


def task_function(task):
    return task.solve()


class ApplyPool:
    def __init__(self, **kwargs):
        self.thread_count = kwargs["thread_count"]
        self.pool = Pool(processes=self.thread_count)

        signal.signal(signal.SIGINT, self.__signal_handler)

    def __signal_handler(self, s, f):
        if self.pool is not None:
            self.pool.terminate()
            exit(s)

    def solve(self, tasks, complexity=1):
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

        while len(res_list) > 0:
            res_list[0].wait()

            i = 0
            while i < len(res_list):
                if res_list[i].ready():
                    res = res_list.pop(i)
                    if res.successful():
                        result.append(res.get())
                    else:
                        rc.debugger.write(0, 1, "Pool solving was completed unsuccessfully")
                        result.append(res.get())
                else:
                    i += 1

            rc.debugger.write(2, 3, "Already solved %d tasks" % len(result))

        return result, now() - start_work_time

    def terminate(self):
        self.pool.close()
