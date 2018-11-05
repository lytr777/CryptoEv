from predictive_function.task import MainTask
from constants.runtime import runtime_constants as rc


class TaskReader:
    def __init__(self, **kwargs):
        self.cg = kwargs["cg"]
        self.backdoor = kwargs["backdoor"]

    def read(self, path_i):
        main_solver = rc.configuration["solvers"].get("main")

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

                tasks.append(MainTask(
                    case=self.cg.generate(self.backdoor, solution),
                    solver=main_solver
                ))

        return tasks

    @staticmethod
    def __from_str(s):
        return [int(c) for c in s]
