from model.solver_report import SolverReport


class LingelingInWrapper:
    statuses = {
        "SATISFIABLE": "SATISFIABLE",
        "UNSATISFIABLE": "UNSATISFIABLE",
        "UNKNOWN": "INDETERMINATE"
    }

    min_time = 0.001

    def __init__(self, solver_path):
        self.solver_path = solver_path

    def get_arguments(self, tl):
        launching_args = [self.solver_path]
        if tl is not None:
            launching_args.append("-T")
            launching_args.append(str(tl))

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
            if output[i].startswith("c ="):
                time = max(float(output[i + 1].split(' ')[4]), self.min_time)
                print time

        solution = solution[:-1]

        report = SolverReport(self.statuses[status], time)
        if status == self.statuses["SATISFIABLE"]:
            report.parse_solution(solution)

        return report

    def set_simplifying(self, flag):
        pass
