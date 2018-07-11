import re
import warnings

from model.solver_report import SolverReport
from wrapper import Wrapper


class CryptoMinisatWrapper(Wrapper):
    statuses = {
        "SATISFIABLE": "SATISFIABLE",
        "UNSATISFIABLE": "UNSATISFIABLE",
        "INDETERMINATE": "INDETERMINATE"
    }

    min_time = 0.01

    def __init__(self):
        info = {
            "tag": "cryptominisat",
            "dir": "cryptominisat",
            "script": "./untar_crypto.sh"
        }
        Wrapper.__init__(self, info)
        self.time_regexp = re.compile('[\t ]+')

    def get_arguments(self, tl=None, workers=None, simplifying=True):
        launching_args = [self.solver_path]

        if tl is not None:
            launching_args.append("--maxtime")
            launching_args.append(str(tl))
        if workers is not None:
            launching_args.append("-t")
            launching_args.append(str(workers))

        return launching_args

    def parse_out(self, output):
        output = output.split('\n')
        solution = ""
        status = ""
        time = self.min_time
        for i in range(len(output)):
            if output[i].startswith("c s") or output[i].startswith("s"):
                status = output[i].split(' ')
                status = status[len(status) - 1]
            if output[i].startswith("v"):
                solution_line = output[i].split(' ')
                for i in range(1, len(solution_line)):
                    solution += solution_line[i] + " "
            if output[i].startswith("c Total time"):
                str_time = output[i].split(": ")[1]
                time = max(float(str_time), self.min_time)

        solution = solution[:-1]

        report = SolverReport(self.statuses[status], time)
        if status == self.statuses["SATISFIABLE"]:
            report.parse_solution(solution)

        return report