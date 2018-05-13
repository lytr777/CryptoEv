import subprocess
import tempfile

import os


class CaseSolver:
    def __init__(self, solver_wrapper):
        self.solver_wrapper = solver_wrapper

    def start(self, args, case):
        tl = args["time_limit"] if ("time_limit" in args) else None
        workers = args["workers"] if ("workers" in args) else None

        l_args = self.solver_wrapper.get_arguments(tl=tl, workers=workers)
        sp = subprocess.Popen(l_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = sp.communicate(case.get_cnf())[0]

        report = self.solver_wrapper.parse_out(output)
        case.mark_solved(report)
