from model.solver_report import SolverReport


class RokkPyWrapper:
    statuses = {
        "SAT": "SATISFIABLE",
        "UNSAT": "UNSATISFIABLE",
        "INDET": "INDETERMINATE"
    }

    def __init__(self, solver_path):
        self.solver_path = solver_path
        self.simplify = True

    def get_arguments(self, tl):
        launching_args = ['python', self.solver_path, '1' if self.simplify else '0']

        if tl is not None:
            launching_args.append(str(tl))

        return launching_args

    def parse_out(self, output):
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

    def set_simplifying(self, flag):
        self.simplify = flag
