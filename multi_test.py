import subprocess
import threading
from time import sleep, time as now

import signal

from parse_utils.cnf_parser import CnfParser
from key_generators.a5_1 import A5_1
from util import caser
from wrapper.cryptominisat import CryptoMinisatWrapper
from wrapper.lingeling import LingelingWrapper

solver_wrapper = CryptoMinisatWrapper(True)
cnf = CnfParser().parse_for_path("./templates/A5_1.cnf")


class TestWorker(threading.Thread):
    def __init__(self, args):
        threading.Thread.__init__(self)
        self.terminated = threading.Event()
        self.data = args["data"]
        self.locks = args["locks"]
        self.need = True

    def run(self):
        while self.need and not self.terminated.isSet():
            self.locks[0].acquire()
            if self.data[0]["N"] > 0:
                self.data[0]["N"] -= 1
                self.locks[0].release()
                self.solve()
            else:
                self.locks[0].release()
                self.need = False

    def solve(self):
        init_case = caser.create_init_case(cnf, A5_1)
        init_args = solver_wrapper.get_arguments(tl=1)

        init_sp = subprocess.Popen(init_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = init_sp.communicate(init_case.get_cnf())
        if len(err) != 0 and not err.startswith("timelimit"):
            raise Exception(err)

        try:
            report = solver_wrapper.parse_out(output)
            init_case.mark_solved(report)
            self.locks[1].acquire()
            self.data[1].append(init_case.time)
            self.locks[1].release()
        except KeyError:
            pass


def __signal_handler(self, s, f):
    for worker in self.workers:
        worker.terminated.set()
    exit(s)


def anyAlive():
    count = 0
    for worker in workers:
        if worker.isAlive():
            count += 1
    return count != 0


N = 100
threads = 2
workers = []

signal.signal(signal.SIGINT, __signal_handler)

counter, times = {"N": N}, []
times_lock = threading.Lock()
worker_args = {
    "data": (counter, times),
    "locks": (threading.Lock(), times_lock)
}

print "start multi test"
print "N = %d" % N
print "threads = %d" % threads

print "init workers"
for i in range(threads):
    workers.append(TestWorker(worker_args))

print "start workers"
for worker in workers:
    worker.start()

start_work_time = now()
while anyAlive():
    sleep(2)
    times_lock.acquire()
    print "solved %d" % len(times)
    times_lock.release()

print "cpu time: %f" % (now() - start_work_time)
print "solved %d/%d with time: %f" % (len(times), N, sum(times) / len(times))
