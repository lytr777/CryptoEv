from model.backdoor import FixedBackdoor as Backdoor
from parser import Parser
from model.case import Case


class TrueLogParserV3(Parser):
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
        assert data[i].startswith("times")
        i += 1
        times = []
        while not data[i].startswith("corrected") and not data[i].startswith("spent"):
            [status, time] = data[i].split(" ")
            times.append((status, float(time)))
            i += 1

        if data[i].startswith("corrected"):
            i += 1

        assert data[i].startswith("spent")
        cpu_time = float(data[i].split(": ")[1])
        assert data[i + 2].startswith("true")
        value = float(data[i + 2].split(": ")[1])

        return info, Case(info["backdoor"], times, value, cpu_time)

    @staticmethod
    def parse_info(info_data):
        get_v = lambda j: info_data[j].split(": ")[1]

        info = {
            "key_generator": get_v(0),
            "solver": get_v(1),
            "pf_type": get_v(2),
        }
        i = 3
        if info["pf_type"] == "ibs":
            info["time_limit"] = int(info_data[i].split(": ")[1])
            i += 1
        info["N"] = get_v(i),
        i += 1
        info["backdoor"] = Backdoor.from_str(get_v(i))

        return info
