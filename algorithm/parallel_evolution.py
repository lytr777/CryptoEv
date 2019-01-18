import warnings
from operator import itemgetter

import numpy as np
from copy import copy
from time import time as now

from constants.runtime import runtime_constants as rc
from algorithm import MetaAlgorithm, Condition
from model.backdoor import Backdoor
from predictive_function.module.selection import RankSelection


class ParallelEvolutionAlgorithm(MetaAlgorithm):
    name = "evolution"

    def __init__(self, **kwargs):
        MetaAlgorithm.__init__(self, **kwargs)
        self.strategy = kwargs["strategy"]
        self.mutation = kwargs["mutation_function"]
        self.crossover = kwargs["crossover_function"]
        self.stagnation_limit = kwargs["stagnation_limit"]
        self.rank_test = kwargs["rank_test"]
        self.rank_cache = {}

        from mpi4py import MPI
        self.comm = MPI.COMM_WORLD
        self.size = self.comm.Get_size()
        self.rank = self.comm.Get_rank()

        if self.size >= self.strategy.get_P_size():
            warnings.warn("bad computation", UserWarning)

    def start(self, backdoor):
        start_time = now()
        rc.debugger.write(0, 0, "MPI Parallel Evolution start on %d nodes" % self.size)

        predictive_f = rc.configuration["predictive_function"]
        selection = predictive_f.selection

        if not str(selection).__contains__("by"):
            raise Exception("Parallel Evolution work only with RankSelections")
        selection.set_mpi_sett(self.size, self.rank)

        if self.rank == 0:
            condition = Condition()
            condition.set("stagnation", 1)
            self.rank_cache = {}

            best, P = self.zero_it(backdoor)
            locals_list = []
            iteration_end = False

            while not self.stop_condition.check(condition):
                self.print_iteration_header(condition.get("iteration"))
                tl = rc.configuration["solvers"].get_tl("main")
                P_v = []

                start_work_time = now()
                while not iteration_end:
                    ps = self.get_ps(best, P, selection)
                    if len(ps) == 0:
                        iteration_end = True
                        continue

                    rc.debugger.write(2, 1, "sending %d backdoors..." % len(ps))
                    for i in range(1, self.size):
                        self.comm.send(ps[i].pack(), dest=i)

                    c_out = predictive_f.compute(ps[0])
                    c_out[0].insert(0, self.rank)

                    mpi_cases = self.comm.gather(c_out[0], root=0)
                    rc.debugger.write(2, 1, "been gathered cases from %d nodes" % len(mpi_cases))

                    keys = set()
                    for cases in mpi_cases:
                        i = cases.pop(0)
                        key = str(ps[i])
                        keys.add(key)
                        if key in self.rank_cache:
                            self.rank_cache[key][0].extend(cases)
                        else:
                            s = len(ps[i])

                            cases = self.rank_test.get_rc(s, tl, cases)
                            self.rank_cache[key] = cases, 1., 1.

                    for key in keys:
                        cases = self.rank_cache[key][0]
                        a, b = self.rank_test.test(best[2], cases)
                        self.rank_cache[key] = cases, a, b

                iteration_end = False
                time = now() - start_work_time
                p_time = time / len(P)

                for p in P:
                    key = str(p)
                    rank_cases = self.rank_cache[key][0]
                    cases = rank_cases.cases
                    r = predictive_f.calculate(p, (cases, p_time))

                    value, pf_log = r[0], r[1]
                    condition.increase("pf_calls")
                    rc.value_hash[key] = value, len(cases)
                    p_v = (p, value, rank_cases)

                    if self.comparator.compare(best, p_v) > 0:
                        best = p_v
                        condition.set("stagnation", -1)

                    P_v.append(p_v)
                    self.print_pf_log(False, key, value, pf_log)

                condition.increase("stagnation")
                if condition.get("stagnation") >= self.stagnation_limit:
                    locals_list.append((best[0], best[1]))
                    condition.increase("local_count")
                    self.print_local_info(best)

                    predictive_f.selection.reset()
                    best, P = self.zero_it(backdoor)
                    condition.set("stagnation", 0)
                else:
                    P_v.sort(cmp=self.comparator.compare)
                    P = self.strategy.get_next_P((self.mutation.mutate, self.crossover.cross), P_v)
                condition.increase("iteration")
                condition.set("time", now() - start_time)

            for i in range(1, self.size):
                self.comm.send([-1, True], dest=i)

            if len(best[0]) != len(backdoor):
                locals_list.append((best[0].snapshot(), best[1]))
                condition.increase("local_count")
                self.print_local_info(best)

            return locals_list
        else:
            while True:
                array = self.comm.recv(source=0)
                if array[0] == -1:
                    break

                p = Backdoor.unpack(array)
                rc.debugger.write(2, 1, "been received backdoor: %s" % p)
                c_out = predictive_f.compute(p)

                rc.debugger.write(2, 1, "sending %d cases... " % len(c_out[0]))
                c_out[0].insert(0, self.rank)
                self.comm.gather(c_out[0], root=0)

    def get_info(self):
        info = MetaAlgorithm.get_info(self)
        info += "-- %s\n" % str(self.strategy)
        info += "-- %s\n" % str(self.mutation)
        info += "-- %s\n" % str(self.crossover)
        info += "-- stagnation limit: %s\n" % str(self.stagnation_limit)
        info += "-- %s\n" % str(self.rank_test)
        return info

    def zero_it(self, backdoor):
        predictive_f = rc.configuration["predictive_function"]

        self.print_iteration_header(0)

        tl = rc.configuration["solvers"].get_tl("main")
        key, s = str(backdoor), len(backdoor)
        if key not in rc.value_hash:
            hashed = False
            start_work_time = now()

            rc.debugger.write(2, 1, "sending backdoor... %s" % backdoor)
            for i in range(1, self.size):
                self.comm.send(backdoor.pack(), dest=i)
            c_out = predictive_f.compute(backdoor)

            mpi_cases = self.comm.gather(c_out[0], root=0)
            rc.debugger.write(2, 1, "been gathered cases from %d nodes" % len(mpi_cases))
            for i in range(1, len(mpi_cases)):
                mpi_cases[i].pop(0)
            cases = np.concatenate(mpi_cases)

            time = now() - start_work_time
            r = predictive_f.calculate(backdoor, (cases, time))

            value, pf_log = r[0], r[1]
            rc.value_hash[key] = value, len(cases)
            rank_cases = self.rank_test.get_rc(s, tl, cases)
            self.rank_cache[key] = rank_cases, 1., 1.
        else:
            hashed = True
            (value, _), pf_log = rc.value_hash[key], ""
            rank_cases = self.rank_cache[key][0]

        self.print_pf_log(hashed, key, value, pf_log)

        P_v = [(backdoor, value)] * max(self.strategy.alive_count, 1)
        P = self.strategy.get_next_P((self.mutation.mutate, self.crossover.cross), P_v)

        return (backdoor, value, rank_cases), P

    def __restart(self, backdoor):
        P = []
        for i in range(self.strategy.get_P_size()):
            P.append(copy(backdoor))

        return P

    def get_ps(self, best, P, sel):
        pr_P = []
        keys = set()

        rtb = self.rank_test.bound
        mx = sel.max_N
        st = sel.chunk_N
        for p in P:
            key = str(p)
            if key not in keys:
                keys.add(key)
                if key not in self.rank_cache:
                    pr_P.append((p, 0))

                    for pr in range(st, mx, st):
                        pr_P.append((p, mx + 1))
                    continue

                cases, pv1, pv2 = self.rank_cache[key]
                if len(cases) == 0:
                    pr_P.append((p, 0))
                elif pv1 < rtb or pv2 < rtb:
                    continue

                for pr in range(len(cases), mx, st):
                    pr_P.append((p, pr + pv2))

        for pr in range(len(best[2]), mx, st):
            pr_P.append((best[0], pr))

        if len(pr_P) < self.size:
            return []

        pr_P.sort(key=itemgetter(1))
        ps = []
        for i in range(self.size):
            ps.append(pr_P[i][0])

        return ps
