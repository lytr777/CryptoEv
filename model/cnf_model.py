class Var:
    def __init__(self, number, negative):
        self.number = number
        self.negative = negative

    def __str__(self):
        return ("-%d" if self.negative else "%d") % self.number


class Clause:
    def __init__(self):
        self.vars = []
        self.max_var = -1

    def add_var(self, var):
        self.vars.append(var)
        self.max_var = max(self.max_var, var.number)
        return self

    def __str__(self):
        s = ""
        for v in self.vars:
            s += "%s " % v
        return s + "0"

    def __len__(self):
        return len(self.vars)


class Cnf:
    def __init__(self):
        self.clauses = []
        self.var_count = 0
        self.edited = True
        self.str = ""

    def add_clause(self, clause):
        self.var_count = max(self.var_count, clause.max_var)
        self.clauses.append(clause)
        self.edited = True
        return self

    def __update_str(self):
        s = ""
        for cl in self.clauses:
            s += "%s\n" % cl
        self.str = s
        self.edited = False

    def __str__(self):
        header = "p cnf %d %d\n" % (self.var_count, self.__len__())
        if self.edited:
            self.__update_str()
        return "%s%s" % (header, self.str)

    def __len__(self):
        return len(self.clauses)

    def to_str(self, substitutions):
        length, sub_str = self.__len__(), ""
        for substitution in substitutions:
            length += len(substitution)
            sub_str += str(substitution)

        header = "p cnf %d %d\n" % (self.var_count, length)
        if self.edited:
            self.__update_str()

        return "%s%s%s" % (header, self.str, sub_str)

    def __copy__(self):
        copy_cnf = Cnf()
        for clause in self.clauses:
            copy_clause = Clause()
            for var in clause.vars:
                copy_var = Var(var.number, var.negative)
                copy_clause.add_var(copy_var)
            copy_cnf.add_clause(copy_clause)
        return copy_cnf


class CnfSubstitution:
    def __init__(self):
        self.clauses = []

    def substitute(self, number, negative):
        var = Var(number, negative)
        self.clauses.append(Clause().add_var(var))
        return self

    def __len__(self):
        return len(self.clauses)

    def __str__(self):
        s = ""
        for cl in self.clauses:
            s += "%s\n" % cl
        return s
