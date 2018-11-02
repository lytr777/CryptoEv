class StopCondition:
    name = "stop_condition"

    def __init__(self, **kwargs):
        self.limit = kwargs["limit"]

    def check(self, cond):
        raise NotImplementedError

    def __str__(self):
        return self.name


class IterationStop(StopCondition):
    def check(self, cond):
        return cond.get("iteration") > self.limit


class PFCallsStop(StopCondition):
    def check(self, cond):
        return cond.get("pf_calls") >= self.limit


class PFValueStop(StopCondition):
    def check(self, cond):
        return cond.get("pf_value") <= self.limit


class LocalsStop(StopCondition):
    def check(self, cond):
        return cond.get("local_count") >= self.limit


class TimeStop(StopCondition):
    time_scale = [1, 60, 60, 24]

    def __init__(self, **kwargs):
        StopCondition.__init__(self, **kwargs)
        self.time = self.__get_seconds(self.limit)

    def check(self, cond):
        return cond.get("time") >= self.time

    def __get_seconds(self, s):
        time_units = s.split(':')[::-1]

        if len(time_units) > len(self.time_scale):
            time_units = time_units[:len(self.time_scale)]

        time, acc = 0, 1
        for i in range(len(time_units)):
            acc *= self.time_scale[i]
            time += int(time_units[i]) * acc

        return time
