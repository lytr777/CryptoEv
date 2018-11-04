import signal

from time import sleep, time as now
from multiprocessing import Pool
from constants.runtime import runtime_constants as rc


def task_function(task):
    return task.solve()


class ApplyPool:
    def __init__(self, **kwargs):
        self.thread_count = kwargs["thread_count"]
        self.task_queue = kwargs["task_queue"]

        self.max_res = self.thread_count * 3
        self.min_res = self.thread_count * 2

        self.pool = Pool(processes=self.thread_count)

        signal.signal(signal.SIGINT, self.__signal_handler)

    def __signal_handler(self, s, f):
        if self.pool is not None:
            self.pool.terminate()
            exit(s)

    def solve(self, filler):
        process_count, remainder = divmod(self.thread_count, filler.get_complexity())

        if process_count == 0 or remainder != 0:
            raise Exception("Incorrect number of threads or workers")
        if process_count != self.thread_count:
            raise Exception("Pool don't support resizing")

        self.task_queue.fill(filler)

        ress = []
        result = []
        start_work_time = now()
        for task in self.task_queue:
            if len(ress) < self.max_res:
                res = self.pool.apply_async(task_function, (task,))
                ress.append(res)
                continue

            while len(ress) > self.min_res:
                ress[0].wait()

                i = 0
                while i < len(ress):
                    if ress[i].ready():
                        if ress[i].successful():
                            res = ress.pop(i)
                            result.append(res.get())
                        else:
                            rc.debugger.write(2, 3, "Pool solving was completed unsuccessfully")
                            raise Exception("Pool solving was completed unsuccessfully")
                    else:
                        i += 1

            rc.debugger.write(2, 3, "Already solved %d tasks" % len(result))

        while len(ress) > 0:
            ress[0].wait()

            i = 0
            while i < len(ress):
                if ress[i].ready():
                    if ress[i].successful():
                        res = ress.pop(i)
                        result.append(res.get())
                    else:
                        rc.debugger.write(2, 3, "Pool solving was completed unsuccessfully")
                        raise Exception("Pool solving was completed unsuccessfully")
                else:
                    i += 1

            rc.debugger.write(2, 3, "Already solved %d tasks" % len(result))

        return result, now() - start_work_time

    def terminate(self):
        self.pool.close()
