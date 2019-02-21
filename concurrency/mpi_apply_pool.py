import errno
import os
import signal
import subprocess

from time import sleep, time as now
from multiprocessing import Pool

from constants.runtime import runtime_constants as rc


def task_function(task):
    return task.solve()


class MPIApplyPool:
    def __init__(self, **kwargs):
        self.thread_count = kwargs["thread_count"]
        self.pool = Pool(processes=self.thread_count)

        from mpi4py import MPI
        self.comm = MPI.COMM_WORLD
        self.size = self.comm.Get_size()
        self.rank = self.comm.Get_rank()

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

        if self.pool is None:
            self.pool = Pool(processes=self.thread_count)

        if self.rank == 0:
            tl = float(rc.best[1]) / (2 ** kwargs['s'])
            self.comm.bcast(tl, root=0)
        else:
            tl = self.comm.bcast(None, root=0)

        wait_time = tl * len(tasks) * self.size / self.thread_count if tl != float("inf") else 1
        wait_time = min(wait_time, float(self.thread_count))
        rc.debugger.write(2, 3, "wait time: %f" % wait_time)

        res_list, result = [], []
        start_work_time = now()
        for task in tasks:
            res = self.pool.apply_async(task_function, (task,))
            res_list.append(res)

        sync_flag, p_time = False, 0.
        while not sync_flag:
            sleep(wait_time)
            p_time += wait_time

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
            time_sum /= (len(tasks) * self.size)

            all_time_sum = self.comm.allgather(time_sum)
            avg_time = sum(all_time_sum)
            if avg_time > tl and len(res_list) > 0:
                rc.debugger.write(2, 3, "Terminate pool (%.2f > %.2f)" % (avg_time, tl))

                # self.pool._taskqueue.mutex.acquire()
                # self.pool._taskqueue.queue.clear()
                # self.pool._taskqueue.mutex.release()

                self.pool.close()
                for worker in self.pool._pool:
                    if worker and worker._popen:
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

                self.pool.terminate()
                self.pool.join()
                self.pool = None

                res_list = []
                left = max(0, len(tasks) - len(result) - p_time_count)
                result.extend([('INDETERMINATE', avg_time + p_time)] * p_time_count)
                result.extend([('INDETERMINATE', 0.)] * left)

            flag = len(res_list) == 0
            all_sync_flag = self.comm.allgather(flag)
            sync_flag = all(all_sync_flag)

        return result, now() - start_work_time

    def terminate(self):
        self.pool.terminate()
