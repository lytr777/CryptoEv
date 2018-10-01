class KeyGenerator:
    key_stream_start = None
    key_stream_len = None

    secret_key_start = None
    secret_key_len = None

    name = None
    tag = None

    short_statuses = {
        "SATISFIABLE": "SAT",
        "UNSATISFIABLE": "UNSAT",
        "INDETERMINATE": "INDET"
    }

    def __init__(self, cnf):
        self.cnf = cnf
        self.substitutions = {}

        self.time = None
        self.status = None
        self.flags = []
        self.solution = []

    def __str__(self):
        return self.name

    def __len__(self):
        return self.key_stream_start + self.key_stream_len - 1

    def add_substitution(self, name, substitution):
        self.substitutions[name] = substitution

    def get_cnf(self):
        return self.cnf.to_str(self.substitutions.values())

    def write_to(self, file_path):
        with open(file_path, 'w+') as f:
            f.write(self.get_cnf())

    def mark_solved(self, report):
        self.time = report.time
        self.status = report.status
        self.flags = report.flags
        self.solution = report.solution

    def check_solution(self):
        if len(self.solution) == 0:
            raise Exception("Solution is not specified")

        if len(self.solution) != self.__len__():
            raise Exception("Solution not corrected")

    def get_status(self, short=False):
        return self.short_statuses[self.status] if short else self.status


class StreamCipher(KeyGenerator):
    def __init__(self, cnf):
        KeyGenerator.__init__(self, cnf)


class BlockCipher(KeyGenerator):
    public_key_start = None
    public_key_len = None

    def __init__(self, cnf):
        KeyGenerator.__init__(self, cnf)
        self.public_key = None


def builder(key_generator):
    def __build(**kwargs):
        return key_generator

    return __build
