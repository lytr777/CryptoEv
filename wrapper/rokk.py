import warnings
import tempfile


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

        solution = ""
        if status == self.statuses["SAT"]:
            i += 2
            solution_line = output[i].split(' ')
            for i in range(1, len(solution_line)):
                solution += solution_line[i] + " "
            solution = solution[:-1]

        with open(out_file, 'w') as f:
            f.write(status[:3] + '\n' + solution)

        return time, status
