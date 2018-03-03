import warnings
import tempfile

from model.solver_report import SolverReport


class RokkWrapper:
    statuses = {
        "SAT": "SATISFIABLE",
        "UNSAT": "UNSATISFIABLE",
        "INDET": "INDETERMINATE"
    }

    def __init__(self, solver_path):
        self.solver_path = solver_path

    def get_arguments(self, cnf, out, time_limit):
        launching_args = [self.solver_path]
        if time_limit is not None:
            warnings.warn("Time limit not support in rokk", UserWarning)

        launching_args.append(cnf)
        launching_args.append(tempfile.gettempdir())

        return launching_args

    def parse_out(self, out_file, output):
        output = output.split('\n')
        time = 0
        i = 0
	# parse SatElite
	k = 0
        for i in range(len(output)):
            if output[i].startswith("c CPU time"):
                time_str = ""
                for s in output[i].split(':')[1]:
                    if s.isdigit() or s == '.':
                        time_str += s
                time += float(time_str)
		k += 1
		if k == 2:
                    break

	time = max(time, 1e-5)
        i += 1
        while not len(output[i]):
            i += 1
        status = output[i].split(' ')[1]

        report = SolverReport(status, time)

        if status == self.statuses["SAT"]:
            i += 2
            solution_line = output[i].split(' ')
            solution = ""
            for i in range(1, len(solution_line)):
                solution += solution_line[i] + " "
            solution = solution[:-1]

            report.parse_solution(solution)

        return report
