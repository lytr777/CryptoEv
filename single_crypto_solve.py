from copy import copy
import numpy as np
from time import time as now

from configuration.options import solvers
from constants import static
from model.backdoor import Backdoor
from key_generators.asg_72_76 import ASG_72_76
from model.case_generator import CaseGenerator
from util.parse.cnf_parser import CnfParser

solver_name = "treengeling"
worker_count = 36

start_j = 1
task_count = 100
backdoor_path = "asg72_bd"
log_path = "./output/_logs/asg_72_76/cryptotask_reports/report_%d"


class BackdoorAssignment:
    def __init__(self, algorithm, backdoor):
        self.algorithm = algorithm
        self.backdoor = backdoor

    def __iter__(self):
        arr = [0] * self.algorithm.secret_key_len

        for key in self.__rec_iter(arr, 0):
            yield key

    def __rec_iter(self, arr, i):
        if i == len(self.backdoor):
            yield copy(arr)
        else:
            for j in [0, 1]:
                arr[self.backdoor.vars[i] - 1] = j
                for key in self.__rec_iter(arr, i + 1):
                    yield key


key_generator = ASG_72_76
cnf_path = static.cnfs[key_generator.tag]
cnf = CnfParser().parse_for_path(cnf_path)

bd = Backdoor.load(backdoor_path)
rs = np.random.RandomState()
cg = CaseGenerator(key_generator, cnf, rs)

solver = solvers[solver_name](
    tl=0,
    simplify=False,
    tag="main",
    workers=worker_count
)

for j in range(start_j, task_count + start_j):
    log_file = open(log_path % j, "w+")

    log_file.write("backdoor: %s\n" % bd)
    log_file.write("solver: %s(%d)\n" % (solver, worker_count))
    log_file.write("\ntasks:\n")
    log_file.flush()

    ba = BackdoorAssignment(key_generator, bd)

    init_case = cg.generate_init()
    init_report = solver.solve(init_case.get_cnf())
    init_case.mark_solved(init_report)

    save_sk = init_case.get_solution_sk()

    start_time, i = now(), 1
    task_solution = init_report.solution
    for key in ba:
        task_solution[:len(key)] = key

        task = cg.generate(bd, task_solution)
        task_report = solver.solve(task.get_cnf())

        log_file.write("%d: %s %f\n" % (i, task_report.status, task_report.time))
        log_file.flush()
        i += 1

        if task_report.status == "SATISFIABLE":
            log_file.write("\ncomparing secret keys:\n")
            log_file.write("%s\n" % save_sk)
            log_file.write("%s\n" % task_report.solution[:len(save_sk)])
            break

    time = now() - start_time
    log_file.write("\ntime: %f\n" % time)
    log_file.write("av time: %f\n" % (time / (i - 1)))
    log_file.close()
