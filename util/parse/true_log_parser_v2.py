from util import formatter
from parser import Parser
from model.case import Case


class TrueLogParserV2(Parser):
    def __init__(self):
        Parser.__init__(self)

    def parse(self, data):
        i = 0
        info_data = []
        while not data[i].startswith("---"):
            info_data.append(data[i])
            i += 1
        i += 1

        info = self.parse_info(info_data)

        cases = []
        case_data = []
        for j in range(i, len(data)):
            if not data[j].startswith("---"):
                case_data.append(data[j])
            elif data[j].startswith("value"):
                break
            elif len(case_data) > 0:
                case = self.parse_case(case_data)
                case_data = []

                cases.append(case)

        return info, cases

    def parse_case(self, case_data):
        assert case_data[0].startswith("start")
        mask = case_data[0].split(": ")[1].split("(")[0]

        assert case_data[1] == "times:"
        i = 2
        times = []
        while not case_data[i].startswith("main"):
            [status, time] = case_data[i].split(" ")
            times.append((status, float(time)))
            i += 1

        assert case_data[i].startswith("main")
        cpu_time = float(case_data[i].split(": ")[1])

        assert case_data[i + 2].startswith("true")
        value = float(case_data[i + 2].split(": ")[1])

        return Case(formatter.format_to_array(mask), times, value, cpu_time)

    @staticmethod
    def parse_info(info_data):
        info = {
            "generator": info_data[0].split(": ")[1],
            "N": int(info_data[1].split("= ")[1])
        }

        return info
