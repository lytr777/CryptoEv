import warnings

from model.solver_report import SolverReport
from wrapper import Wrapper


class RokkWrapper(Wrapper):
    statuses = {
        "SAT": "SATISFIABLE",
        "UNSAT": "UNSATISFIABLE",
        "INDET": "INDETERMINATE"
    }

    def __init__(self, tl_util):
        info = {
            "tag": "rokk",
            "dir": "rokk",
            "script": "./untar_rokk.sh"
        }
        Wrapper.__init__(self, info, tl_util)

    def get_common_arguments(self, tl, workers, simplifying):
        launching_args = ['python', self.solver_path, '1' if simplifying else '0', '0']

        if tl is not None:
            launching_args.append(str(tl))
        if workers is not None:
            warnings.warn("Workers not support in ROKK", UserWarning)

        return launching_args

    def get_timelimit_arguments(self, tl, workers, simplifying):
        launching_args = ['python', self.solver_path, '1' if simplifying else '0', '1', str(tl)]

        if workers is not None:
            warnings.warn("Workers not support in ROKK", UserWarning)

        return launching_args

    def parse_out(self, output, algorithm):
        data = output.split('\n')

        split_time = data[0].split(' ')
        if (len(split_time) == 2) and split_time[1] == 'p':
            report = SolverReport(data[1], float(split_time[0]))
            report.set_flag(0, True)
        else:
            report = SolverReport(data[1], float(data[0]))

        if data[1] == self.statuses['SAT']:
            report.parse_solution(data[2])

        return report
