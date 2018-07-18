import subprocess
from multiprocessing import Pool
from time import time as now

from parse_utils.cnf_parser import CnfParser
from key_generators.a5_1 import A5_1
from util import caser
from wrapper.cryptominisat import CryptoMinisatWrapper
from wrapper.lingeling import LingelingWrapper


def solve(k):
    init_case = caser.create_init_case(cnf, A5_1)
    init_args = solver_wrapper.get_arguments(tl=1)

    init_sp = subprocess.Popen(init_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = init_sp.communicate(init_case.get_cnf())
    if len(err) != 0 and not err.startswith("timelimit"):
        raise Exception(err)

    try:
        report = solver_wrapper.parse_out(output)
        init_case.mark_solved(report)
        return init_case.time
    except KeyError:
        return None


solver_wrapper = CryptoMinisatWrapper(True)
cnf = CnfParser().parse_for_path("./templates/A5_1.cnf")

N = 100
threads = 2
pool = Pool(processes=threads)

print "start multi pool test"
print "N = %d" % N
print "threads = %d" % threads

start_work_time = now()

times = []
for time in pool.map(solve, range(N)):
    if time is not None:
        times.append(time)

print "cpu time: %f" % (now() - start_work_time)
print "solved %d/%d with time: %f" % (len(times), N, sum(times) / len(times))