class Var:
    def __init__(self, number, negative):
        self.number = number
        self.negative = negative

    def __str__(self):
        return ("-" if self.negative else "") + str(self.number)


class Clause:
    def __init__(self):
        self.vars = []

    def add_var(self, var):
        self.vars.append(var)

    def get_max_var_number(self):
        m = 0
        for v in self.vars:
            m = max(m, v.number)
        return m

    def __str__(self):
        s = ""
        for v in self.vars:
            s += str(v) + " "
        return s + "0"


class Cnf:
    def __init__(self):
        self.clauses = []
        self.var_count = 0

    def add_clause(self, clause):
        self.var_count = max(self.var_count, clause.get_max_var_number())
        self.clauses.append(clause)

    def __str__(self):
        s = ""
        for cl in self.clauses:
            s += str(cl) + "\n"
        return "p cnf " + str(self.var_count) + " " + str(len(self.clauses)) + "\n" + s

    def __copy__(self):
        copy_cnf = Cnf()
        for clause in self.clauses:
            copy_clause = Clause()
            for var in clause.vars:
                copy_var = Var(var.number, var.negative)
                copy_clause.add_var(copy_var)
            copy_cnf.add_clause(copy_clause)
        return copy_cnf
