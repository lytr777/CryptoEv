import numpy as np
from time import time as now

from algorithm import MetaAlgorithm
from model.backdoor_list import BackdoorList
from model.case_generator import CaseGenerator
from model.variable_set import Backdoor
from parse_utils.cnf_parser import CnfParser
from util import constant


class MPIEvolutionAlgorithm(MetaAlgorithm):
    name = "MPI Evolution Algorithm"

    def __init__(self, ev_parameters, comm):
        MetaAlgorithm.__init__(self, ev_parameters)
        self.mutation_f = ev_parameters["mutation_function"]
        self.crossover_f = ev_parameters["crossover_function"]
        self.stagnation_limit = ev_parameters["stagnation_limit"]
        self.strategy = ev_parameters["evolution_strategy"]
        self.comm = comm
        self.size = comm.Get_size()
        self.rank = comm.Get_rank()

    def start(self, mf_parameters):
        algorithm = mf_parameters["key_generator"]
        cnf_path = constant.cnfs[algorithm.tag]
        cnf = CnfParser().parse_for_path(cnf_path)
        cg = CaseGenerator(algorithm, cnf)
        mf_parameters["mpi_call"] = True

        backdoor = Backdoor(algorithm, self.init_backdoor.vars)
        cg.set_backdoor(backdoor)

        (quotient, remainder) = divmod(mf_parameters["N"], self.size)
        rank_N = quotient + (1 if remainder > 0 else 0)
        real_N = rank_N * self.size

        mf_parameters["N"] = rank_N
        if self.rank == 0:
            max_value = float("inf")
            it = 1
            mf_calls = 0
            stagnation = 0

            P = self.__restart()
            best = (BackdoorList(), max_value, [])
            locals_list = []

            self.print_info(algorithm.name, "%s" % self.strategy)

            while not self.stop_condition(it, mf_calls, len(locals_list), best[1]):
                self.print_iteration_header(it)
                P_v = []
                for p in P:
                    backdoor.from_list(p)
                    key = p.get_key()
                    if key in self.value_hash:
                        hashed = True
                        (value, n), mf_log = self.value_hash[key], ""
                        p_v = (p, value)
                    else:
                        hashed = False
                        start_work_time = now()

                        self.comm.Bcast(p.value_list, root=0)
                        mf = self.predictive_function(mf_parameters)
                        result = mf.compute(cg)

                        cases = self.comm.gather(result[2], root=0)
                        cases = np.concatenate(cases)

                        time = now() - start_work_time
                        final_result = mf.handle_cases(cg, cases, time)

                        value, mf_log = final_result[0], final_result[1]
                        mf_calls += 1
                        self.value_hash[key] = value, real_N
                        p_v = (p, value)

                        if self.comparator(best, p_v) > 0:
                            best = p_v
                            stagnation = -1

                    P_v.append(p_v)
                    self.print_mf_log(hashed, key, value, mf_log)

                stagnation += 1
                if stagnation >= self.stagnation_limit:
                    P = self.__restart()
                    locals_list.append(best)
                    self.print_local_info(best)
                    best = (BackdoorList(), max_value, [])
                    stagnation = 0
                else:
                    P_v.sort(cmp=self.comparator)
                    P = self.strategy.get_next_population((self.mutation_f, self.crossover_f), P_v)
                it += 1

            self.comm.Bcast(np.array([-1] * algorithm.secret_key_len), root=0)

            if best[1] != max_value:
                locals_list.append(best)
                self.print_local_info(best)

            return locals_list
        else:
            while True:
                value_list = np.empty(len(self.init_backdoor), dtype=np.int)
                self.comm.Bcast(value_list, root=0)
                if value_list.__contains__(-1):
                    break

                p = backdoor.to_list()
                p.value_list = value_list
                backdoor.from_list(p)

                mf = self.predictive_function(mf_parameters)
                result = mf.compute(cg)

                self.comm.gather(result[2], root=0)

    def __restart(self):
        P = []
        for i in range(self.strategy.get_population_size()):
            P.append(self.init_backdoor.to_list())

        return P
