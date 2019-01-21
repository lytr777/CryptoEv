import os

from constants.static import error_path
from datetime import datetime


def trace_solver_error(name, title, cnf, output, error):
    filename = '%s_%s' % (name, datetime.today())
    filename = filename.replace(' ', '_')
    path = os.path.join(error_path, filename)

    with open(path, 'w+') as f:
        f.write(__check_n(title))
        f.write("------------------------- CNF -------------------------\n")
        f.write(__check_n(cnf))
        f.write("------------------------ OUTPUT ------------------------\n")
        f.write(__check_n(output))
        f.write("------------------------ ERROR ------------------------\n")
        f.write(__check_n(error))


def __check_n(s):
    s = str(s)
    if s[-1] == '\n':
        return s
    return s + '\n'
