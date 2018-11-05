from constants.runtime import runtime_constants as rc


class TrueTask:
    def __init__(self, **kwargs):
        self.case = kwargs["case"]
        self.solvers = kwargs["solvers"]

    def solve(self):
        report = self.solvers.solve("main", self.case.get_cnf())
        self.case.mark_solved(report)

        return self.case.get_status(short=True), self.case.time


class TaskReader:
    def __init__(self, **kwargs):
        self.cg = kwargs["cg"]
        self.backdoor = kwargs["backdoor"]

    def read(self, path_i):
        solvers = rc.configuration["solvers"]

        tasks = []
        with open(path_i, 'r') as f:
            lines = f.readlines()

            for line in lines:
                line = line[:-1]
                [bd_str, ks_str] = line.split(" -> ")

                solution_len = self.cg.key_stream.max
                solution = [0] * solution_len

                self.backdoor.set_values(solution, self.__from_str(bd_str))
                self.cg.key_stream.set_values(solution, self.__from_str(ks_str))

                case = self.cg.generate(self.backdoor, solution)

                tasks.append(TrueTask(
                    case=case,
                    solvers=solvers
                ))

        return tasks

    @staticmethod
    def __from_str(s):
        return [int(c) for c in s]
