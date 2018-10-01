

class StopCondition:
    def __init__(self, **kwargs):
        self.limit = kwargs["limit"]

    def check(self, cond):
        raise NotImplementedError


class IterationStop(StopCondition):
    def check(self, cond):
        return cond.get("iteration") > self.limit
