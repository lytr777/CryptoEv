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


if __name__ == '__main__':
    from time import time as now

    times, count = [], 10
    for k in range(1, count):
        t1 = now()
        cnf = CnfParser().parse_for_path('./templates/Salsa20.cnf')
        times.append(now() - t1)
        if k % (count / 10) == 0: print '%d%%' % (k * 100 / count)

    print(sum(times) / len(times))
