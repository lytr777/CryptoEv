from model.cnf_model import CnfSubstitution


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
        self.substitutions = []

        self.time = None
        self.status = None
        self.flags = []
        self.solution = []

    def __str__(self):
        return self.name

    def add_substitution(self, name, substitution):
        self.substitutions.append(substitution)
        # print "add substitution for %s" % name

    def get_cnf(self):
        return self.cnf.to_str(self.substitutions)

    def write_to(self, file_path):
        with open(file_path, 'w') as f:
            f.write(self.get_cnf())

    def mark_solved(self, report):
        self.time = report.time
        self.status = report.status
        self.flags = report.flags
        self.solution = report.solution

    def check_solution(self):
        if len(self.solution) == 0:
            raise Exception("Solution is not specified")

        true_solution_len = self.key_stream_start + self.key_stream_len - 1
        if len(self.solution) != true_solution_len:
            raise Exception("Solution not corrected")

    def get_status(self, short=False):
        return self.short_statuses[self.status] if short else self.status
