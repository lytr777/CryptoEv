from model.solver_report import SolverReport
from wrapper import Wrapper


class PainlessWrapper(Wrapper):
    statuses = {
        "SATISFIABLE": "SATISFIABLE",
        "UNSATISFIABLE": "UNSATISFIABLE",
        "UNKNOWN": "INDETERMINATE"
    }

    min_time = 0.001

    def __init__(self, tl_util):
        info = {
            "tag": "painless",
            "dir": "painless",
            "script": "./untar_painless.sh"
        }
        Wrapper.__init__(self, info, tl_util)

    def get_common_arguments(self, workers, tl, simplifying):
        launching_args = ["python", "./tools/stdin_to_file.py"]
        launching_args.extend([self.solver_path, "-c=%d" % workers])

        if tl is not None:
            launching_args.append("-t=%d" % tl)

        return launching_args

    def get_timelimit_arguments(self, workers, tl, simplifying):
        launching_args = ["python", "./tools/stdin_to_file.py"]
        launching_args.extend(["timelimit", "-t%d" % tl, self.solver_path, "-c=%d" % workers])

        return launching_args

    def parse_out(self, output):
        output = output.split('\n')
        status, time, solution = "", self.min_time, ""
        for i in range(len(output)):
            if output[i].startswith("c s") or output[i].startswith("s"):
                status = output[i].split(' ')[-1]
            if output[i].startswith("c Resolution time: "):
                str_time = output[i].split(": ")[1]
                time = max(float(str_time[:-1]), self.min_time)
            if output[i].startswith("v"):
                solution_line = output[i].split(' ')
                for var in solution_line[1:]:
                    solution += "%s " % var

        if status == "":
            return SolverReport(self.statuses["UNKNOWN"], -1)

        report = SolverReport(self.statuses[status], time)
        if status == self.statuses["SATISFIABLE"]:
            report.parse_solution(solution[:-1], self.spaces)

        return report
