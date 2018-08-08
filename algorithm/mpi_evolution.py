import numpy as np
from time import time as now

from algorithm import MetaAlgorithm
from model.case_generator import CaseGenerator
from parse_utils.cnf_parser import CnfParser
from util import constant


class MPIEvolutionAlgorithm(MetaAlgorithm):
    name = "evolution"

    def __init__(self, ev_parameters, comm):
        MetaAlgorithm.__init__(self, ev_parameters)
        self.mutation_f = ev_parameters["mutation_function"]
        self.crossover_f = ev_parameters["crossover_function"]
        self.stagnation_limit = ev_parameters["stagnation_limit"]
        self.strategy = ev_parameters["evolution_strategy"]
        self.comm = comm
        self.size = comm.Get_size()
        self.rank = comm.Get_rank()

    def start(self, pf_parameters):
        algorithm = pf_parameters["key_generator"]
        cnf_path = constant.cnfs[algorithm.tag]
        cnf = CnfParser().parse_for_path(cnf_path)

        rs = np.random.RandomState(43)
        cg = CaseGenerator(algorithm, cnf, rs, self.backdoor)
        pf_parameters["mpi_call"] = True

        (quotient, remainder) = divmod(pf_parameters["N"], self.size)
        rank_N = quotient + (1 if remainder > 0 else 0)
        real_N = rank_N * self.size

        pf_parameters["N"] = rank_N
        if self.rank == 0:
            max_value = float("inf")
            it = 1
            pf_calls = 0
            stagnation = 0

            P = self.__restart()
            best = (self.backdoor.get(), max_value, [])
            locals_list = []

            solver = pf_parameters["solver_wrapper"].info["tag"]
            tl = pf_parameters["time_limit"] if self.p_function.type == "ibs" else None
            self.print_info(algorithm.tag, solver, tl, str(self.strategy))

            while not self.stop_condition(it, pf_calls, len(locals_list), best[1]):
                self.print_iteration_header(it)
                P_v = []
                for p in P:
                    self.backdoor.set(p)
                    key = str(self.backdoor)
                    if key in self.value_hash:
                        hashed = True
                        (value, n), pf_log = self.value_hash[key], ""
                        p_v = (p, value)
                    else:
                        hashed = False
                        start_work_time = now()

                        self.comm.Bcast(p, root=0)
                        pf = self.p_function(pf_parameters)
                        result = pf.compute(cg)

                        cases = self.comm.gather(result[2], root=0)
                        cases = np.concatenate(cases)

                        time = now() - start_work_time
                        final_result = pf.handle_cases(cg, cases, time)

                        value, pf_log = final_result[0], final_result[1]
                        pf_calls += 1
                        self.value_hash[key] = value, real_N
                        p_v = (p, value)

                        if self.comparator(best, p_v) > 0:
                            best = p_v
                            stagnation = -1

                    P_v.append(p_v)
                    self.print_pf_log(hashed, key, value, pf_log)

                stagnation += 1
                if stagnation >= self.stagnation_limit:
                    locals_list.append((self.backdoor.snapshot(best[0]), best[1]))
                    self.print_local_info(best)
                    P = self.__restart()
                    best = (self.backdoor.get(), max_value, [])
                    stagnation = 0
                else:
                    P_v.sort(cmp=self.comparator)
                    P = self.strategy.get_next_population((self.mutation_f, self.crossover_f), P_v)
                it += 1

            self.comm.Bcast(np.array([-1] * algorithm.secret_key_len), root=0)

            if best[1] != max_value:
                locals_list.append((self.backdoor.snapshot(best[0]), best[1]))
                self.print_local_info(best)

            return locals_list
        else:
            while True:
                p = np.empty(self.backdoor.length, dtype=np.int)
                self.comm.Bcast(p, root=0)
                if p.__contains__(-1):
                    break

                self.backdoor.set(p)
                pf = self.p_function(pf_parameters)
                result = pf.compute(cg)

                self.comm.gather(result[2], root=0)

    def __restart(self):
        P = []
        self.backdoor.reset()
        for i in range(self.strategy.get_population_size()):
            P.append(self.backdoor.get())

        return P
