from model.solver_report import SolverReport
from util.parser import parse_solution_file

class MinisatWrapper:
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
            launching_args.append("-cpu-lim=" + str(time_limit))

        launching_args.append(cnf)
        launching_args.append(out)

        return launching_args

    def parse_out(self, out_file, output):
        output = output.split('\n')
        time = 0
        i = 0
        for i in range(len(output)):
            if output[i].startswith("CPU time"):
                time_str = ""
                for s in output[i].split(':')[1]:
                    if s.isdigit() or s == '.':
                        time_str += s
                time = float(time_str)
                break

        i += 1
        while not len(output[i]):
            i += 1
        status = output[i]

        solution = parse_solution_file(out_file)

        report = SolverReport(status, time)
        if status == self.statuses["SAT"]:
            report.parse_solution(solution)

        return report
