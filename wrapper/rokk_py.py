from model.solver_report import SolverReport


class RokkPyWrapper:
    statuses = {
        "SAT": "SATISFIABLE",
        "UNSAT": "UNSATISFIABLE",
        "INDET": "INDETERMINATE"
    }

    def __init__(self, solver_path):
        self.solver_path = solver_path

    def get_arguments(self, cnf, out, time_limit):
        launching_args = ['python', self.solver_path]

        launching_args.append(cnf)
        if time_limit is not None:
            launching_args.append(time_limit)

        return launching_args

    def parse_out(self, out_file, output):
        data = output.split('\n')

        report = SolverReport(data[1], float(data[0]))
        if data[1] == self.statuses['SAT']:
            report.parse_solution(data[2])

        return report
