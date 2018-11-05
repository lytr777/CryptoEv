import signal

from time import sleep, time as now
from multiprocessing import Pool
from constants.runtime import runtime_constants as rc


def task_function(task):
    return task.solve()


class MapPool:
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

        start_work_time = now()
        result = self.pool.map_async(task_function, tasks)

        while not result.ready():
            result.wait()

        if result.successful():
            return result.get(), now() - start_work_time
        else:
            rc.debugger.write(0, 1, "Pool solving was completed unsuccessfully")
            raise Exception("Pool solving was completed unsuccessfully")

    def terminate(self):
        self.pool.close()
