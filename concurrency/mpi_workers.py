import os
import signal
import subprocess

from multiprocessing import Process, Queue
from time import sleep, time as now
from constants.runtime import runtime_constants as rc


def worker_cycle(task_queue, result_queue):
    while True:
        if not task_queue.empty():
            task = task_queue.get()
            result = task.solve()

            result_queue.put(result)


class MPIWorkers:
    def __init__(self, **kwargs):
        self.thread_count = kwargs["thread_count"]

        self.task_queue = Queue()
        self.result_queue = Queue()

        self.workers = []

        from mpi4py import MPI
        self.comm = MPI.COMM_WORLD
        self.size = self.comm.Get_size()
        self.rank = self.comm.Get_rank()

        signal.signal(signal.SIGINT, self.__signal_handler)

    def __signal_handler(self, s, f):
        self.terminate()
        exit(s)

    def __create_workers(self, count):
        count = min(count, self.thread_count - len(self.workers))

        for i in range(count):
            worker = Process(
                target=worker_cycle,
                args=(
                    self.task_queue,
                    self.result_queue
                )
            )
            self.workers.append(worker)
            worker.daemon = True
            worker.start()

    def __kill_workers(self, count):
        count = min(count, len(self.workers))

        killed_workers = []
        for i in range(count):
            worker = self.workers.pop()
            worker.terminate()
            killed_workers.append(worker)

        for worker in killed_workers:
            if worker.is_alive():
                worker.join()

    def solve(self, tasks, complexity=1, **kwargs):
        worker_count, remainder = divmod(self.thread_count, complexity)

        if worker_count == 0 or remainder != 0:
            raise Exception("Incorrect number of threads or workers")

        if self.rank == 0:
            tl = float(rc.best[1]) / (2 ** kwargs['s'])
            self.comm.bcast(tl, root=0)
        else:
            tl = self.comm.bcast(None, root=0)

        wait_time = tl * len(tasks) * self.size / self.thread_count if tl != float("inf") else 1
        wait_time = min(wait_time, float(self.thread_count))
        rc.debugger.write(2, 3, "wait time: %f" % wait_time)

        if len(self.workers) != worker_count:
            diff = worker_count - len(self.workers)
            if diff > 0:
                self.__create_workers(diff)
            else:
                self.__kill_workers(-diff)

        self.__clear_queue(self.result_queue)

        start_work_time = now()
        for task in tasks:
            self.task_queue.put(task, False)

        res_list = []
        sync_flag, p_time = False, 0.
        while not sync_flag:
            sleep(wait_time)
            p_time += wait_time

            while not self.result_queue.empty():
                p_time = 0.
                res = self.result_queue.get(False)
                res_list.append(res)

            left_len = len(tasks) - len(res_list)
            p_time_count = min(self.thread_count, left_len)

            time_sum = p_time * p_time_count
            for _, time in res_list:
                time_sum += float(time)
            time_sum /= (len(tasks) * self.size)

            rc.debugger.write(2, 3, "Already solved %d of %d tasks" % (len(res_list), len(tasks)))

            all_time_sum = self.comm.allgather(time_sum)
            avg_time = sum(all_time_sum)

            if avg_time > tl and left_len > 0:
                rc.debugger.write(2, 3, "Terminate workers (%.2f > %.2f)" % (avg_time, tl))

                self.__clear_queue(self.task_queue)

                for worker in self.workers:
                    ppid = worker._popen.pid
                    spc = subprocess.Popen("pgrep -P %d" % ppid, shell=True,
                                           stdout=subprocess.PIPE)
                    ps_out = spc.stdout.read()
                    spc.wait()
                    for pid in ps_out.strip().split("\n"):
                        try:
                            os.kill(int(pid), signal.SIGTERM)
                        except OSError:
                            pass
                        except ValueError:
                            pass

                self.terminate()

                left = max(0, len(tasks) - len(res_list) - p_time_count)
                res_list.extend([('INDETERMINATE', avg_time + p_time)] * p_time_count)
                res_list.extend([('INDETERMINATE', 0.)] * left)

                left_len = len(tasks) - len(res_list)

            flag = left_len == 0
            all_sync_flag = self.comm.allgather(flag)
            sync_flag = all(all_sync_flag)

        end_work_time = now()

        self.__clear_queue(self.task_queue)
        self.__clear_queue(self.result_queue)

        return res_list, end_work_time - start_work_time

    def terminate(self):
        self.__kill_workers(len(self.workers))

    @staticmethod
    def __clear_queue(queue):
        while not queue.empty():
            queue.get(False)
