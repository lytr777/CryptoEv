import numpy as np
from copy import copy
from time import time as now

from constants.runtime import runtime_constants as rc
from algorithm import MetaAlgorithm, Condition
from model.backdoor import Backdoor


class MPISimulatedAnnealing(MetaAlgorithm):
    name = "simulated annealing (mpi)"

    def __init__(self, **kwargs):
        MetaAlgorithm.__init__(self, **kwargs)
        self.start_T = kwargs["start_T"]
        self.ro = kwargs["ro"]
        self.Q = kwargs["Q"]

        from mpi4py import MPI
        self.comm = MPI.COMM_WORLD
        self.size = self.comm.Get_size()
        self.rank = self.comm.Get_rank()

    def start(self, backdoor):
        start_time = now()
        rc.debugger.write(0, 0, "MPI Simulated Annealing start on %d nodes" % self.size)

        predictive_f = rc.configuration["predictive_function"]
        predictive_f.selection.set_mpi_sett(self.size, self.rank)

        if self.rank == 0:
            condition = Condition()
            condition.set("temperature", self.start_T)
            max_value = float("inf")
            updated_logs = {}

            X = [copy(backdoor), copy(backdoor)]

            if str(backdoor) in rc.value_hash:
                rc.best = (backdoor, rc.value_hash[str(backdoor)][0], [])
            else:
                rc.best = (backdoor, max_value, [])

            while not self.stop_condition.check(condition):
                self.print_iteration_header(condition.get("iteration"), "T: %.2f" % condition.get("temperature"))
                X_v = []
                for x in X:
                    key = str(x)
                    if key in rc.value_hash:
                        hashed = True
                        if key in updated_logs:
                            logs = updated_logs[key]
                            updated_logs.pop(key)
                        else:
                            logs = ""

                        (value, _), pf_log = rc.value_hash[key], logs

                        x_v = (x, value)
                    else:
                        hashed = False
                        start_work_time = now()

                        rc.debugger.write(2, 1, "sending backdoor... %s" % x)
                        self.comm.bcast(x.pack(), root=0)
                        c_out = predictive_f.compute(x)

                        cases = self.comm.gather(c_out[0], root=0)
                        rc.debugger.write(2, 1, "been gathered cases from %d nodes" % len(cases))
                        cases = np.concatenate(cases)

                        time = now() - start_work_time
                        r = predictive_f.calculate(x, (cases, time))

                        value, pf_log = r[0], r[1]
                        condition.increase("pf_calls")
                        rc.value_hash[key] = value, len(cases)
                        x_v = (x, value)

                        if self.comparator.compare(rc.best, x_v) > 0:
                            rc.best = x_v

                    X_v.append(x_v)
                    self.print_pf_log(hashed, key, value, pf_log)

                X_v.sort(cmp=self.comparator.compare)
                X = self.__simulate(X_v, condition)
                condition.increase("iteration")
                condition.set("time", now() - start_time)

            self.comm.bcast([-1, True], root=0)

            condition.increase("local_count")
            self.print_local_info(rc.best)

            return [(rc.best[0].snapshot(), rc.best[1])]
        else:
            while True:
                array = self.comm.bcast(None, root=0)
                if array[0] == -1:
                    break

                p = Backdoor.unpack(array)
                rc.debugger.write(2, 1, "been received backdoor: %s" % p)
                c_out = predictive_f.compute(p)

                rc.debugger.write(2, 1, "sending %d cases... " % len(c_out[0]))
                self.comm.gather(c_out[0], root=0)

    def get_info(self):
        info = MetaAlgorithm.get_info(self)
        info += "-- Q: %s\n" % str(self.Q)
        info += "-- ro: %s\n" % str(self.ro)
        info += "-- start T: %s\n" % str(self.start_T)
        return info

    def __get_point(self, x):
        new_v = x.get_mask()
        for i in range(self.ro):
            j = np.random.randint(x.length)
            new_v[j] = not new_v[j]

        return x.get_copy(new_v)

    def __simulate(self, X_v, condition):
        X, T = [], condition.get("temperature")
        if X_v[0][1] > X_v[1][1]:
            X.append(X_v[1][0])
        else:
            pr = np.exp((X_v[0][1] - X_v[1][1]) / T)
            p = np.random.rand()
            if p < pr:
                X.append(X_v[1][0])
            else:
                X.append(X_v[0][0])

        X.append(self.__get_point(X[0]))
        condition.set("temperature", T * self.Q)
        return X
