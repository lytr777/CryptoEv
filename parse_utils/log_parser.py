from util import formatter
from parser import Parser
from model.case import Case


def parse_ibs_case(case_data):
    st_line = case_data[0]
    if st_line.startswith("start") or st_line.startswith("update"):
        mask = st_line.split(" ")[4].split("(")[0]
        assert case_data[1] == "times:"
        i = 2
        times = []
        while not case_data[i].startswith("time limit") and not case_data[i].startswith("main"):
            [status, time] = case_data[i].split(" ")
            times.append((status, float(time)))
            i += 1

        if case_data[i].startswith("time limit"):
            i += 1

        assert case_data[i].startswith("main")
        cpu_time = float(case_data[i].split(": ")[1])
        assert case_data[i + 2].startswith("end")
        value = float(case_data[i + 2].split(": ")[1])

        return Case(formatter.format_to_array(mask), times, value, cpu_time)
    elif st_line.startswith("mask"):
        mask = st_line.split(" ")[1].split("(")[0]

        assert case_data[1].startswith("with")
        value = float(case_data[1].split(": ")[1])

        return Case(formatter.format_to_array(mask), [], value, 0)
    else:
        raise Exception("unexpected line: %s" % st_line)


def parse_gad_case(case_data):
    st_line = case_data[0]
    if st_line.startswith("start") or st_line.startswith("update"):
        mask = st_line.split(" ")[4].split("(")[0]
        assert case_data[4] == "times:"
        i = 5
        times = []
        while not case_data[i].startswith("main"):
            [status, time] = case_data[i].split(" ")
            times.append((status, float(time)))
            i += 1

        assert case_data[i].startswith("main")
        cpu_time = float(case_data[i].split(": ")[1])
        assert case_data[i + 2].startswith("end")
        value = float(case_data[i + 2].split(": ")[1])

        return Case(formatter.format_to_array(mask), times, value, cpu_time)
    elif st_line.startswith("mask"):
        mask = st_line.split(" ")[1].split("(")[0]

        assert case_data[1].startswith("with")
        value = float(case_data[1].split(": ")[1])

        return Case(formatter.format_to_array(mask), [], value, 0)
    else:
        raise Exception("unexpected line: %s" % st_line)


class LogParser(Parser):
    case_parsers = {
        "ibs": parse_ibs_case,
        "gad": parse_gad_case
    }

    def __init__(self, function_name):
        Parser.__init__(self)
        self.case_parser = self.case_parsers[function_name]

    def parse(self, data):
        i = 0
        info_data = []
        while not data[i].startswith("---"):
            info_data.append(data[i])
            i += 1
        i += 1

        info = self.parse_info(info_data)

        iterations = []
        it_data = []
        for j in range(i, len(data)):
            if data[j].startswith("best"):
                break
            elif not data[j].startswith("iteration"):
                it_data.append(data[j])
            elif len(it_data) > 0:
                cases = self.parse_iteration(it_data)
                it_data = []

                iterations.append(cases)

        if len(it_data) > 0:
            cases = self.parse_iteration(it_data)
            iterations.append(cases)

        return info, iterations

    def parse_iteration(self, it_data):
        cases = []
        case_data = []
        for i in range(len(it_data)):
            if not it_data[i].startswith("---"):
                case_data.append(it_data[i])
            elif len(case_data) > 0:
                case = self.case_parser(case_data)
                case_data = []

                cases.append(case)

        return cases

    @staticmethod
    def parse_info(info_data):
        info = {"algorithm": info_data[0].split(" ")[1]}

        i = 1
        if info["algorithm"] == "Evolution":
            st_args = info_data[i].split(" ", 2)
            info["strategy"] = {
                "type": st_args[1],
                "param": st_args[2]
            }
            i += 1

        info["start_s"] = int(info_data[i].split("= ")[1])
        i += 1
        info["generator"] = info_data[i].split(": ")[1]
        return info
