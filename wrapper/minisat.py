from model.solver_report import SolverReport
from util.constant import solver_paths


class MinisatWrapper:
    statuses = {
        "SAT": "SATISFIABLE",
        "UNSAT": "UNSATISFIABLE",
        "INDET": "INDETERMINATE"
    }

    tag = "minisat"

    def __init__(self):
        self.solver_path = solver_paths[self.tag]

    def get_arguments(self, cnf, out, tl):
        launching_args = [self.solver_path]
        if tl is not None:
            launching_args.append("-cpu-lim=" + str(tl))

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

        with open(out_file) as f:
            lines = f.readlines()
            if lines[0] == "SAT\n":
                solution = lines[1][:-1]
            else:
                solution = ""

        report = SolverReport(status, time)
        if status == self.statuses["SAT"]:
            report.parse_solution(solution)

        return report

    def set_simplifying(self, flag):
        pass
