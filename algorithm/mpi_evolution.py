import numpy as np
from copy import copy
from time import time as now

from constants.runtime import runtime_constants as rc
from algorithm import MetaAlgorithm, Condition
from model.backdoor import Backdoor
from model.case_generator import CaseGenerator
from util.parse.cnf_parser import CnfParser
from constants import static


class MPIEvolutionAlgorithm(MetaAlgorithm):
    name = "evolution (mpi)"

    def __init__(self, **kwargs):
        MetaAlgorithm.__init__(self, **kwargs)
        self.strategy = kwargs["strategy"]
        self.mutation = kwargs["mutation_function"]
        self.crossover = kwargs["crossover_function"]
        self.stagnation_limit = kwargs["stagnation_limit"]

        from mpi4py import MPI
        self.comm = MPI.COMM_WORLD
        self.size = self.comm.Get_size()
        self.rank = self.comm.Get_rank()

    def start(self, backdoor):
        rc.debugger.write(0, 0, "MPI Evolution start on %d nodes" % self.size)

        predictive_f = rc.configuration["predictive_function"]
        key_generator = predictive_f.key_generator
        cnf_path = static.cnfs[key_generator.tag]
        cnf = CnfParser().parse_for_path(cnf_path)
        rs = np.random.RandomState(43)

        cg = CaseGenerator(key_generator, cnf, rs)

        predictive_f.selection.set_mpi_sett(self.size, self.rank)

        if self.rank == 0:
            condition = Condition()
            condition.set("stagnation", 1)
            max_value = float("inf")
            updated_logs = {}

            P = self.__restart(backdoor)
            best = (backdoor, max_value, [])
            locals_list = []

            while not self.stop_condition.check(condition):
                self.print_iteration_header(condition.get("iteration"))
                P_v = []
                for p in P:
                    key = str(p)
                    if key in rc.value_hash:
                        hashed = True
                        if key in updated_logs:
                            logs = updated_logs[key]
                            updated_logs.pop(key)
                        else:
                            logs = ""

                        (value, _), pf_log = rc.value_hash[key], logs

                        p_v = (p, value)
                    else:
                        hashed = False
                        start_work_time = now()

                        packed_p = p.pack()
                        rc.debugger.write(2, 1, "sending backdoor... %s" % packed_p)
                        self.comm.bcast(packed_p, root=0)
                        c_out = predictive_f.compute(cg, p)

                        cases = self.comm.gather(c_out[0], root=0)
                        rc.debugger.write(2, 1, "receive cases from %d nodes" % len(cases))
                        cases = np.concatenate(cases)

                        time = now() - start_work_time
                        r = predictive_f.calculate(cg, p, (cases, time))

                        value, pf_log = r[0], r[1]
                        condition.increase("pf_calls")
                        rc.value_hash[key] = value, len(cases)
                        p_v = (p, value)

                        if self.comparator.compare(best, p_v) > 0:
                            best = p_v
                            condition.set("stagnation", -1)

                    P_v.append(p_v)
                    self.print_pf_log(hashed, key, value, pf_log)

                condition.increase("stagnation")
                if condition.get("stagnation") >= self.stagnation_limit:
                    locals_list.append((best[0], best[1]))
                    condition.increase("local_count")
                    self.print_local_info(best)
                    P = self.__restart(backdoor)

                    predictive_f.selection.reset()
                    best = (backdoor, max_value, [])
                    condition.set("stagnation", 0)
                else:
                    P_v.sort(cmp=self.comparator.compare)
                    P = self.strategy.get_next_population((self.mutation.mutate, self.crossover.cross), P_v)
                condition.increase("iteration")

            self.comm.bcast([-1, True], root=0)

            if best[1] != max_value:
                locals_list.append((best[0].snapshot(), best[1]))
                condition.increase("local_count")
                self.print_local_info(best)

            return locals_list
        else:
            while True:
                array = self.comm.bcast(None, root=0)
                rc.debugger.write(2, 1, "receive backdoor: %s" % array)
                if array[0] == -1:
                    break

                p = Backdoor.unpack(array)
                c_out = predictive_f.compute(cg, p)

                rc.debugger.write(2, 1, "sending %d cases... " % len(c_out))
                self.comm.gather(c_out[0], root=0)

    def get_info(self):
        info = MetaAlgorithm.get_info(self)
        info += "-- %s\n" % str(self.strategy)
        info += "-- %s\n" % str(self.mutation)
        info += "-- %s\n" % str(self.crossover)
        info += "-- stagnation limit: %s\n" % str(self.stagnation_limit)
        return info

    def __restart(self, backdoor):
        P = []
        for i in range(self.strategy.get_population_size()):
            P.append(copy(backdoor))

        return P
