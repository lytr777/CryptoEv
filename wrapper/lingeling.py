from model.solver_report import SolverReport


class LingelingWrapper:
    statuses = {
        "SATISFIABLE": "SATISFIABLE",
        "UNSATISFIABLE": "UNSATISFIABLE",
        "UNKNOWN": "INDETERMINATE"
    }

    min_time = 0.1

    def __init__(self, solver_path):
        self.solver_path = solver_path

    def get_arguments(self, cnf, out, time_limit):
        launching_args = [self.solver_path]
        if time_limit is not None:
            launching_args.append("-T")
            launching_args.append(str(time_limit))

        launching_args.append(cnf)

        return launching_args

    def parse_out(self, out_file, output):
        output = output.split('\n')
        solution = ""
        status = ""
        for out_line in output:
            if out_line.startswith("c s") or out_line.startswith("s"):
                status = out_line.split(' ')
                status = status[len(status) - 1]
            if out_line.startswith("v"):
                solution_line = out_line.split(' ')
                for i in range(1, len(solution_line)):
                    solution += solution_line[i] + " "
        solution = solution[:-1]

        if len(output) < 2 or len(output[len(output) - 2].split(' ')) < 2:
            with open('out/incorrect_lingelin_out', 'w') as f:
                for out_line in output:
                    f.write(out_line + '\n')
            time = self.min_time
        else:
            time = max(float(output[len(output) - 2].split(' ')[1]), self.min_time)

        report = SolverReport(self.statuses[status], time)
        if status == self.statuses["SATISFIABLE"]:
            report.parse_solution(solution)

        return report
