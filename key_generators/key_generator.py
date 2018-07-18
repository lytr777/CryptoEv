from model.cnf_model import CnfSubstitution


class KeyGenerator:
    key_stream_start = None
    key_stream_len = None

    secret_key_start = None
    secret_key_len = None

    short_statuses = {
        "SATISFIABLE": "SAT",
        "UNSATISFIABLE": "UNSAT",
        "INDETERMINATE": "INDET"
    }

    def __init__(self, cnf):
        self.cnf = cnf
        self.substitution = CnfSubstitution()

        self.key_stream = None
        self.secret_key = None
        self.secret_mask = None

        self.time = None
        self.status = None
        self.flags = []
        self.solution = []

    def set_key_stream(self, key):
        if self.key_stream_len != len(key):
            raise Exception("Key stream must contain %d bits" % self.key_stream_len)

        self.key_stream = key

    def set_secret_key(self, key, mask):
        if self.secret_key_len != len(key):
            raise Exception("Secret key must contain %d bits" % self.secret_key_len)

        if len(mask) != len(key):
            raise Exception("Secret mask must contain %d bits" % self.secret_key_len)

        self.secret_key = key
        self.secret_mask = mask

    def __substitute_key_stream(self):
        for i in range(len(self.key_stream)):
            self.substitution.substitute(self.key_stream_start + i, not self.key_stream[i])

    def __substitute_secret_key(self):
        for i in range(len(self.secret_key)):
            if self.secret_mask[i]:
                self.substitution.substitute(self.secret_key_start + i, not self.secret_key[i])

    def write_to(self, file_path):
        with open(file_path, 'w') as f:
            f.write(self.get_cnf())

    def get_cnf(self):
        if self.key_stream is not None:
            self.__substitute_key_stream()
        if self.secret_key is not None:
            self.__substitute_secret_key()

        return self.cnf.to_str(self.substitution)

    def mark_solved(self, report):
        self.time = report.time
        self.status = report.status
        self.flags = report.flags
        self.solution = report.solution

    def get_status(self, short=False):
        if short:
            return self.short_statuses[self.status]
        else:
            return self.status

    def get_solution_secret_key(self):
        start = self.secret_key_start - 1
        end = start + self.secret_key_len
        return self.__get_key(start, end)

    def get_solution_key_stream(self):
        start = self.key_stream_start - 1
        end = start + self.key_stream_len
        return self.__get_key(start, end)

    def __get_key(self, start, end):
        if len(self.solution) == 0:
            raise Exception("Solution is not specified")

        true_solution_len = self.key_stream_start + self.key_stream_len - 1
        if len(self.solution) != true_solution_len:
            raise Exception("Solution not corrected")

        return self.solution[start:end]
