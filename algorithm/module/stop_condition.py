

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
