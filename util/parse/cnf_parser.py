from model.cnf import Cnf
from parser import Parser


class CnfParser(Parser):
    def __init__(self):
        Parser.__init__(self)

    def parse(self, data):
        cnf = Cnf()
        for line in data:
            line = line.strip()
            if (line[0].isdigit()) or (line[0].startswith('-')):
                clause = [int(n) for n in line.split(' ')]
                if clause[-1] == 0:
                    clause.pop(-1)

                cnf.add_clause(clause)

        return cnf
