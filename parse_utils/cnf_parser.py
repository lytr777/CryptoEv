from model.cnf_model import Cnf, Clause, Var
from parse_utils.parser import Parser


class CnfParser(Parser):
    def __init__(self):
        Parser.__init__(self)

    def parse(self, data):
        cnf = Cnf()
        for line in data:
            line = line.strip()
            clause = Clause()
            if (line[0].isdigit()) or (line[0].startswith("-")):
                for num in line.split():
                    num_int = int(num)
                    if num_int < 0:
                        clause.add_var(Var(abs(num_int), True))
                    elif num_int > 0:
                        clause.add_var(Var(abs(num_int), False))
                cnf.add_clause(clause)

        return cnf
