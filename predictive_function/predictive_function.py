from constants.runtime import runtime_constants as rc


class PredictiveFunction:
    type = None

    def __init__(self, **kwargs):
        self.chunk_size = kwargs["chunk_size"]
        self.selection = kwargs["selection"]
        self.key_generator = kwargs["key_generator"]

    def compute(self, backdoor, cases):
        raise NotImplementedError

    def calculate(self, backdoor, compute_out):
        raise NotImplementedError

    def correct_selection(self, backdoor, value, cases):
        old_N, new_N = self.selection.correct_by((backdoor, value, cases))
        if old_N != new_N:
            rc.debugger.write(1, 0, "selection size changed from %d to %d" % (old_N, new_N))

    def get_time_stat(self, cases):
        time_stat = {
            "DETERMINATE": 0,
            "INDETERMINATE": 0
        }
        cases_log = "times:\n"
        for info in cases:
            cases_log += "%s %s\n" % (info[0], info[1])
            self.__update_time_statistic(time_stat, info[0])

        return time_stat, cases_log

    @staticmethod
    def __update_time_statistic(time_stat, status):
        if status == "UNSAT" or status == "SAT":
            time_stat["DETERMINATE"] += 1
        else:
            time_stat["INDETERMINATE"] += 1
