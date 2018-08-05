from util import formatter


class MetaAlgorithm:
    name = None

    def __init__(self, parameters):
        self.log_file = parameters["log_file"]
        self.locals_log_file = parameters["locals_log_file"]

        self.init_backdoor = parameters["init_backdoor"]
        self.comparator = parameters["comparator"]
        self.predictive_function = parameters["predictive_function"]
        self.stop_condition = parameters["stop_condition"]
        self.value_hash = parameters["value_hash"]

    def start(self, mf_parameters):
        raise NotImplementedError

    def print_info(self, alg_name, info=None):
        with open(self.log_file, 'a') as f:
            f.write("-- %s\n" % self.name)
            if info is not None:
                f.write("-- %s\n" % info)
            f.write("-- Start with backdoor: %s\n" % self.init_backdoor)
            f.write("-- Key Generator: %s\n" % alg_name)

    def print_iteration_header(self, it):
        with open(self.log_file, 'a') as f:
            f.write("------------------------------------------------------\n")
            f.write("iteration step: %d\n" % it)

    def print_mf_log(self, hashed, key, value, mf_log):
        with open(self.log_file, 'a') as f:
            f.write("------------------------------------------------------\n")
            if hashed:
                if mf_log == "":
                    f.write("mask: %s has been saved in hash\n" % key)
                    f.write("with value: %.7g\n" % value)
                else:
                    f.write("update prediction with mask: %s\n" % key)
                    f.write(mf_log)
                    f.write("end prediction with value: %.7g\n" % value)
            else:
                f.write("start prediction with mask: %s\n" % key)
                f.write(mf_log)
                f.write("end prediction with value: %.7g\n" % value)

    def print_local_info(self, local):
        with open(self.locals_log_file, 'a') as f:
            f.write("------------------------------------------------------\n")
            f.write("local with mask: %s\n" % formatter.format_array(local[0]))
            f.write("and value: %.7g\n" % local[1])
