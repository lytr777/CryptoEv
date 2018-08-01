class DispersionFunction:
    def compute(self, lines):
        raise NotImplementedError


class RelativeDeviation(DispersionFunction):
    def __init__(self, parameters):
        self.ad = parameters["allowable_deviation"]
        self.av_count = parameters["average_count"]

    def compute(self, lines):
        original = lines.pop()
        av_buffs = []
        min_value = original[len(original) - 1]
        for k in range(len(lines)):
            av_buffs.append([])

        for i in range(len(original)):
            for j in range(len(lines)):
                diff = abs(original[i] - lines[j][i])
                rd = diff * 100. / original[i]

                if i == 0:
                    for k in range(self.av_count):
                        av_buffs[j].append(rd)
                else:
                    av_buffs[j].pop(0)
                    av_buffs[j].append(rd)

                av_rd = (sum(av_buffs[j]) / self.av_count)
                if av_rd > self.ad:
                    if i > 0:
                        j = i - 1
                        while original[i] == original[j]:
                            j -= 1
                        return original[j]
                    return original[i]

        return min_value


class DispersionAnalyzer:
    def __init__(self, f, max_value):
        self.f = f
        self.max_value = max_value

    def analyze(self, k_tuples):
        values = [self.max_value]
        keys = sorted(k_tuples.keys())

        for key in keys:
            _, lines = k_tuples[key]
            values.append(self.f.compute(lines))

        return values
