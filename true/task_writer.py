import os
from time import time as now

from constants.runtime import runtime_constants as rc


class TaskWriter:
    def __init__(self, **kwargs):
        self.chuck_size = kwargs["chuck_size"]
        self.cg = kwargs["cg"]
        self.backdoor = kwargs["backdoor"]

    def prepare(self):
        init_cases = []
        for j in range(self.chuck_size):
            init_cases.append(self.cg.generate_init())

        return init_cases

    def write(self, path_i, init_cases):
        solvers = rc.configuration["solvers"]
        file_i = open(path_i, "w+")

        for init_case in init_cases:
            init_report = solvers.solve("init", init_case.get_cnf())

            init_case.mark_solved(init_report)

            bd_value = self.backdoor.get_values(init_case.solution)
            ks_value = self.cg.key_stream.get_values(init_case.solution)
            bs_str, ks_str = self.__to_str(bd_value), self.__to_str(ks_value)
            file_i.write("%s -> %s\n" % (bs_str, ks_str))

        file_i.close()
        return path_i

    @staticmethod
    def __to_str(array):
        return ''.join(str(e) for e in array)

    @staticmethod
    def clean(*files):
        for file_i in files:
            os.remove(file_i)
