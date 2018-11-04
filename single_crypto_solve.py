from copy import copy
import numpy as np
from time import time as now

from concurrency.workers import Workers
from constants import static
from model.backdoor import Backdoor, SecretKey
from key_generators.asg_72_76 import ASG_72_76
from model.case_generator import CaseGenerator
from solver.lingeling import LingelingSolver
from util.parse.cnf_parser import CnfParser


class BackdoorSort:
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
bd = Backdoor.load("backdoor")
bs = BackdoorSort(key_generator, bd)

cnf_path = static.cnfs[key_generator.tag]
cnf = CnfParser().parse_for_path(cnf_path)
rs = np.random.RandomState(43)

cg = CaseGenerator(key_generator, cnf, rs)
solver = LingelingSolver(
    tl=0,
    simplify=False,
    tag="main"
)

init_case = cg.generate_init()
init_report = solver.solve(init_case.get_cnf())
init_case.mark_solved(init_report)

save_sk = init_case.get_solution_sk()

start_time = now()
task_solution = init_report.solution
for key in bs:
    task_solution[:len(key)] = key

    task = cg.generate(bd, task_solution)
    task_report = solver.solve(task.get_cnf())

    print task_report.status, task_report.time

    if task_report.status == "SATISFIABLE":
        break

print now() - start_time
