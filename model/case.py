class Case:
    def __init__(self, mask, times, value, cpu_time):
        self.mask = mask
        self.times = times
        self.value = value
        self.cpu_time = cpu_time

    def mt(self):
        return self.mask, self.times

    def mv(self):
        return self.mask, self.value

    def mvt(self):
        return self.mask, self.value, self.times

    def get_statistic(self):
        statistic = {
            "DETERMINATE": 0,
            "INDETERMINATE": 0
        }

        for status, _ in self.times:
            if status == "SAT" or status == "UNSAT":
                statistic["DETERMINATE"] += 1
            else:
                statistic["INDETERMINATE"] += 1

        return statistic

    def __str__(self):
        return "%s for %s" % (self.value, self.mask)
