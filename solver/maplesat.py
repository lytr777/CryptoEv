import warnings

from solver import Solver
from model.solver_report import SolverReport


class MapleSATSolver(Solver):
    statuses = {
        "SATISFIABLE": "SATISFIABLE",
        "UNSATISFIABLE": "UNSATISFIABLE",
        "UNKNOWN": "INDETERMINATE"
    }

    min_time = 0.01

    def __init__(self, **kwargs):
        info = {
            "name": "maplesat",
            "dir": "maplesat",
            "script": "./untar_maplesat.sh"
        }
        Solver.__init__(self, info, **kwargs)

    def get_arguments(self, l_args, workers, tl, simp):
        l_args.append(self.solver_path)

        if tl > 0:
            l_args.append("-cpu-lim=%d" % tl)
        if workers != 1:
            warnings.warn("workers not support in maplesat", UserWarning)

        return l_args

    def parse_out(self, output):
        output = output.split('\n')
        i = 0
        while not output[i].startswith("CPU time"):
            i += 1

        str_time = output[i].split(": ")[1]
        time = max(float(str_time[:-1]), self.min_time)

        status = output[i + 2]

        report = SolverReport(self.statuses[status], time)
        # if status == self.statuses["SATISFIABLE"]:
        #     report.parse_solution(solution, self.spaces)

        return report

# |  Number of variables:          4010                                         |
# |  Number of clauses:           17658                                         |
# |  Parse time:                   0.01 s                                       |
# |  Eliminated clauses:           0.43 Mb                                      |
# |  Simplification time:          0.05 s                                       |
# |                                                                             |
# LBD Based Clause Deletion : 1
# Rapid Deletion : 1
# Almost Conflict : 1
# Anti Exploration : 1
# ============================[ Search Statistics ]==============================
# | Conflicts |          ORIGINAL         |          LEARNT          | Progress |
# |           |    Vars  Clauses Literals |    Limit  Clauses Lit/Cl |          |
# ===============================================================================
# ===============================================================================
# restarts              : 1
# conflicts             : 0              (0 /sec)
# decisions             : 1              (0.00 % random) (17 /sec)
# propagations          : 0              (0 /sec)
# conflict literals     : 0              (-nan % deleted)
# actual reward         : -nan
# Memory used           : 9.00 MB
# CPU time              : 0.058991 s
#
# SATISFIABLE
