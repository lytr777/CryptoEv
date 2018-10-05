from constants.runtime import runtime_constants as rc


class MetaAlgorithm:
    name = None

    def __init__(self, **kwargs):
        self.comparator = kwargs["comparator"]
        self.stop_condition = kwargs["stop_condition"]

    def start(self, init_backdoor):
        raise NotImplementedError

    def get_info(self):
        return "-- algorithm: %s\n" % self.name

    def print_iteration_header(self, it):
        rc.logger.write("------------------------------------------------------\n",
                        "iteration step: %d\n" % it)

    def print_pf_log(self, hashed, key, value, pf_log):
        rc.logger.deferred_write("------------------------------------------------------\n")
        if hashed:
            if pf_log == "":
                rc.logger.write("hashed backdoor: %s\n" % key,
                                "with value: %.7g\n" % value)
            else:
                rc.logger.write("update prediction with backdoor: %s\n" % key,
                                pf_log, "end prediction with value: %.7g\n" % value)
        else:
            rc.logger.write("start prediction with backdoor: %s\n" % key,
                            pf_log, "end prediction with value: %.7g\n" % value)

    def print_local_info(self, local):
        print "------------------------------------------------------"
        print "local with backdoor: %s" % local[0]
        print "and value: %.7g" % local[1]


class Condition:
    def __init__(self):
        self.conditions = {
            "iteration": 1,
            "pf_calls": 0,
            "pf_value": float("inf"),
            "local_count": 0
        }

    def set(self, key, value):
        self.conditions[key] = value

    def increase(self, key):
        self.conditions[key] += 1

    def get(self, key):
        return self.conditions[key]
