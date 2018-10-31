from model.backdoor import FixedBackdoor as Backdoor
from parser import Parser
from model.case import Case


class LogParserV3(Parser):
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

        iterations = []
        it_data = []
        for j in range(i, len(data)):
            if data[j].startswith("value"):
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
                case = self.parse_case(case_data)
                case_data = []

                cases.append(case)

        return cases

    @staticmethod
    def parse_case(case_data):
        st_line = case_data[0]
        if st_line.startswith("start") or st_line.startswith("update"):
            backdoor = Backdoor.from_str(st_line.split(": ")[1])
            assert case_data[1].startswith("times")
            i = 2
            times = []
            while not case_data[i].startswith("corrected") and not case_data[i].startswith("spent"):
                [status, time] = case_data[i].split(" ")
                times.append((status, float(time)))
                i += 1

            if case_data[i].startswith("corrected"):
                i += 1

            assert case_data[i].startswith("spent")
            cpu_time = float(case_data[i].split(": ")[1])
            assert case_data[i + 2].startswith("end")
            value = float(case_data[i + 2].split(": ")[1])

            return Case(backdoor, times, value, cpu_time)
        elif st_line.startswith("hashed"):
            backdoor = Backdoor.from_str(st_line.split(": ")[1])

            assert case_data[1].startswith("with")
            value = float(case_data[1].split(": ")[1])

            return Case(backdoor, [], value, 0)
        else:
            raise Exception("Unexpected line: %s" % st_line)

    @staticmethod
    def parse_info(info_data):
        def get_v(j, k=1):
            return info_data[j].split(": ")[k]

        get_n = lambda j: get_v(j, 0).split("-- ")[1]

        info = {}
        for i in range(len(info_data)):
            info[get_n(i)] = get_v(i)
        # info = {"algorithm": get_v(0)}
        # i = 1
        # if info["algorithm"] == "evolution":
        #     info["strategy"] = {"type": get_n(i), "param": get_v(i)}
        #     i += 1
        # for key in ["key_generator", "solver", "pf_type"]:
        #     info[key] = get_v(i)
        #     i += 1
        # if info["pf_type"] == "ibs":
        #     info["time_limit"] = int(info_data[i].split(": ")[1])
        #     i += 1
        # info["backdoor"] = Backdoor.from_str(get_v(i))

        return info
