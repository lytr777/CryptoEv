from util import formatter


class SolverReport:
    def __init__(self, status, time):
        self.time = time
        self.status = status
        self.solution = []
        self.flags = [
            False  # preprocessing
        ]

    def parse_solution(self, solution_str):
        data = solution_str.split(" ")

        for var in data:
            num_int = int(var)
            if num_int < 0:
                self.solution.append(0)
            elif num_int > 0:
                self.solution.append(1)

    def set_flag(self, i, value):
        self.flags[i] = value

    def __str__(self):
        return "%s (%f) solution: %s" % (self.status, self.time, formatter.format_array(self.solution))
