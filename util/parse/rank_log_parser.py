from model.backdoor import FixedBackdoor as Backdoor
from parser import Parser
from model.case import Case


class RankLogParser(Parser):
    def __init__(self, tl):
        self.tl = tl
        Parser.__init__(self)

    def parse(self, data):
        i = 1
        iterations = []
        it_data = []
        while i < len(data):
            if data[i].startswith("--"):
                i += 1
                continue

            if data[i].startswith("iteration"):
                tests = self.parse_iteration(it_data)
                it_data = []
                i += 1

                iterations.append(tests)
            else:
                test = []
                for j in range(3):
                    test.append(data[i])
                    i += 1
                it_data.append(test)

        if len(it_data) > 0:
            tests = self.parse_iteration(it_data)
            iterations.append(tests)

        return iterations

    def parse_iteration(self, it_data):
        cases = []
        for test in it_data:
            assert len(test) == 3

            [bd1_str, s1] = test[0].split(': ')
            bd1 = Backdoor.from_str(bd1_str)
            case1 = self.parse_case(bd1, s1)

            [bd2_str, s2] = test[1].split(': ')
            bd2 = Backdoor.from_str(bd2_str)
            case2 = self.parse_case(bd2, s2)

            [a, b] = test[2].split(': ')[1][1:-1].split(', ')
            cases.append((case1, case2, a, b))

        return cases

    def parse_case(self, bd, s):
        s = s[1:-1]
        case_str, j = [], 0
        for i in range(len(s)):
            if s[i] == ',' and s[i + 1] == ' ' and (s[i - 1] == ']' or s[i - 1] == ')'):
                case_str.append(s[j:i])
                j = i + 2

        times = []
        det, indet = 0., 0.
        for st_str in case_str:
            if st_str[0] == '[':
                [status, time] = st_str[1:-1].split(' ')
                times.append((status[1:-1], float(time[1:-1])))
            else:
                [status, time] = st_str[1:-1].split(', ')
                times.append((status[1:-1], float(time)))

            if status == 'INDET':
                indet += 1
            else:
                det += 1

        xi = det / (det + indet)
        if xi != 0:
            value = (2 ** len(bd)) * self.tl * (3 / xi)
        else:
            value = float('inf')

        return Case(bd, times, value, 0.)
