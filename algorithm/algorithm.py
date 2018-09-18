class MetaAlgorithm:
    name = None

    def __init__(self, parameters):
        self.log_file = parameters["log_file"]

        self.init_backdoor = parameters["init_backdoor"]
        self.comparator = parameters["comparator"]
        self.p_function = parameters["predictive_function"]
        self.stop_condition = parameters["stop_condition"]
        self.value_hash = parameters["value_hash"]

    def start(self, pf_parameters):
        raise NotImplementedError

    def print_info(self, alg_name, solver_name, tl=None, info=None):
        with open(self.log_file, 'a') as f:
            f.write("-- algorithm: %s\n" % self.name)
            if info is not None:
                f.write("-- %s\n" % info)
            f.write("-- key generator: %s\n" % alg_name)
            f.write("-- solver: %s\n" % solver_name)
            f.write("-- pf type: %s\n" % self.p_function.type)
            if tl is not None:
                f.write("-- time limit: %s\n" % tl)
            f.write("-- backdoor: %s\n" % self.init_backdoor)

    def print_iteration_header(self, it):
        with open(self.log_file, 'a') as f:
            f.write("------------------------------------------------------\n")
            f.write("iteration step: %d\n" % it)

    def print_pf_log(self, hashed, key, value, pf_log):
        with open(self.log_file, 'a') as f:
            f.write("------------------------------------------------------\n")
            if hashed:
                if pf_log == "":
                    f.write("hashed backdoor: %s\n" % key)
                    f.write("with value: %.7g\n" % value)
                else:
                    f.write("update prediction with backdoor: %s\n" % key)
                    f.write(pf_log)
                    f.write("end prediction with value: %.7g\n" % value)
            else:
                f.write("start prediction with backdoor: %s\n" % key)
                f.write(pf_log)
                f.write("end prediction with value: %.7g\n" % value)

    def print_local_info(self, local):
        print "------------------------------------------------------"
        print "local with backdoor: %s" % local[0]
        print "and value: %.7g" % local[1]
