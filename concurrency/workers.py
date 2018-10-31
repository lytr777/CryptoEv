import threading
import signal

from copy import copy
from time import sleep, time as now
from constants.runtime import runtime_constants as rc


class Worker(threading.Thread):
    def __init__(self, **kwargs):
        threading.Thread.__init__(self)
        self.terminated = threading.Event()

        self.task_cond = kwargs["task_cond"]
        self.task_queue = kwargs["task_queue"]
        self.result_lock = kwargs["result_lock"]
        self.result_list = kwargs["result_list"]

    def run(self):
        while not self.terminated.isSet():
            self.task_cond.acquire()
            while len(self.task_queue) == 0:
                self.task_cond.wait()

                if self.terminated.isSet():
                    break

            if len(self.task_queue) == 0:
                self.task_cond.release()
            else:
                task = self.task_queue.pop()
                self.task_cond.release()
                result = task.solve()

                self.result_lock.acquire()
                self.result_list.append(result)
                self.result_lock.release()


class Workers:
    def __init__(self, **kwargs):
        self.thread_count = kwargs["thread_count"]
        self.task_queue = kwargs["task_queue"]

        self.task_cond = threading.Condition()
        self.result_lock = threading.Lock()

        self.result_list = []
        self.workers = []
        self.sleep_time = 2

        signal.signal(signal.SIGINT, self.__signal_handler)

    def __signal_handler(self, s, f):
        self.terminate()
        exit(s)

    def __create_workers(self, count):
        count = min(count, self.thread_count - len(self.workers))

        for i in range(count):
            worker = Worker(
                task_cond=self.task_cond,
                task_queue=self.task_queue,
                result_lock=self.result_lock,
                result_list=self.result_list
            )
            self.workers.append(worker)
            worker.start()

    def __kill_workers(self, count):
        count = min(count, len(self.workers))

        killed_workers = []
        for i in range(count):
            worker = self.workers.pop()
            worker.terminated.set()
            killed_workers.append(worker)

        self.task_cond.acquire()
        self.task_cond.notify_all()
        self.task_cond.release()

        for worker in killed_workers:
            if worker.isAlive():
                worker.join()

    def solve(self, filler):
        worker_count, remainder = divmod(self.thread_count, filler.get_complexity())

        if worker_count == 0 or remainder != 0:
            raise Exception("Incorrect number of threads or workers")

        if len(self.workers) != worker_count:
            diff = worker_count - len(self.workers)
            if diff > 0:
                self.__create_workers(diff)
            else:
                self.__kill_workers(-diff)

        self.result_lock.acquire()
        if len(self.result_list) > 0:
            self.__clear_list(self.result_list)
        self.result_lock.release()

        self.task_cond.acquire()
        self.task_queue.fill(filler)
        self.task_cond.notify_all()
        self.task_cond.release()

        start_work_time = now()
        task_count = filler.get_count()
        result_len = 0

        while task_count > result_len:
            sleep(self.sleep_time)
            self.result_lock.acquire()
            result_len = len(self.result_list)
            self.result_lock.release()

            self.task_cond.acquire()
            queue_len = len(self.task_queue)
            self.task_cond.release()

            rc.debugger.write(2, 3, "solved %d of %d (in queue: %d)" % (result_len, task_count, queue_len))

        end_work_time = now()
        solved = copy(self.result_list)

        self.__clear_list(self.result_list)

        return solved, end_work_time - start_work_time

    def terminate(self):
        self.__kill_workers(len(self.workers))

    @staticmethod
    def __clear_list(l):
        while len(l) > 0:
            l.pop()
