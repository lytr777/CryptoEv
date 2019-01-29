from copy import copy


class Cnf:
    def __init__(self):
        self.clauses = []
        self.max_var = 0
        self.edited = True
        self.str = ""

    def add_clause(self, clause):
        self.max_var = max(self.max_var, max(clause))
        self.clauses.append(clause)
        self.edited = True
        return self

    def __update_str(self):
        s = ""
        for cl in self.clauses:
            s += "%s 0\n" % ' '.join([str(n) for n in cl])
        self.str = s
        self.edited = False

    def __str__(self):
        header = "p cnf %d %d\n" % (self.max_var, len(self))
        if self.edited:
            self.__update_str()
        return "%s%s" % (header, self.str)

    def __len__(self):
        return len(self.clauses)

    def to_str(self, substitutions):
        length, sub_str = len(self), ""
        for substitution in substitutions:
            length += len(substitution)
            sub_str += str(substitution)

        header = "p cnf %d %d\n" % (self.max_var, length)
        if self.edited:
            self.__update_str()

        return "%s%s%s" % (header, self.str, sub_str)

    def __copy__(self):
        copy_cnf = Cnf()
        for clause in self.clauses:
            copy_clause = copy(clause)
            copy_cnf.clauses.append(copy_clause)
        copy_cnf.max_var = self.max_var
        copy_cnf.edited = self.edited
        copy_cnf.str = self.str
        return copy_cnf


class CnfSubstitution:
    def __init__(self):
        self.vars = []

    def substitute(self, var):
        self.vars.append(var)
        return self

    def __len__(self):
        return len(self.vars)

    def __str__(self):
        s = ""
        for var in self.vars:
            s += "%d 0\n" % var
        return s
