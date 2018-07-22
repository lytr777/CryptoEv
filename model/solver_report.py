import re

import sys

from util import formatter


class SolverReport:
    def __init__(self, status, time):
        self.time = time
        self.status = status
        self.solution = []
        self.flags = [
            False  # preprocessing
        ]

    def parse_solution(self, solution_str, spaces=re.compile('[\t ]+')):
        solution_str = solution_str.strip()
        data = spaces.split(solution_str)

        try:
            for var in data:
                num_int = int(var)
                if num_int < 0:
                    self.solution.append(0)
                elif num_int > 0:
                    self.solution.append(1)
        except ValueError:
            with open("out/solution_error_log", "w+") as f:
                f.write("Solution: %s\n" % formatter.format_array(self.solution))
                f.write("Solution len: %d\n\n" % len(self.solution))
                f.write(sys.exc_info()[0])
                f.write("\n\n")
                f.write(solution_str)
            # raise ValueError(sys.exc_info()[0])

    def set_flag(self, i, value):
        self.flags[i] = value

    def __str__(self):
        return "%s (%f) solution: %s" % (self.status, self.time, formatter.format_array(self.solution))
