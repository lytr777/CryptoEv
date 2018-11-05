import os
from time import time as now

from constants.runtime import runtime_constants as rc


class TaskWriter:
    def __init__(self, **kwargs):
        self.chuck_size = kwargs["chuck_size"]
        self.cg = kwargs["cg"]
        self.backdoor = kwargs["backdoor"]

    def write(self, path_i):
        solvers = rc.configuration["solvers"]

        s_time, w_time = 0, 0
        file_i = open(path_i, "w+")

        print "start write to: %s" % path_i
        for j in range(self.chuck_size):
            init_case = self.cg.generate_init()
            cnf_j = init_case.get_cnf()

            s1 = now()
            init_report = solvers.solve("init", cnf_j)
            s_time += now() - s1

            init_case.mark_solved(init_report)

            w1 = now()
            bd_value = self.backdoor.get_values(init_case.solution)
            ks_value = self.cg.key_stream.get_values(init_case.solution)
            bs_str, ks_str = self.__to_str(bd_value), self.__to_str(ks_value)
            file_i.write("%s -> %s\n" % (bs_str, ks_str))
            w_time += now() - w1

        file_i.close()
        return path_i

    @staticmethod
    def __to_str(array):
        return ''.join(str(e) for e in array)

    @staticmethod
    def clean(*files):
        for file_i in files:
            os.remove(file_i)
