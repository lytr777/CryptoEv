from constants.runtime import runtime_constants as rc


class Task:
    def __init__(self, **kwargs):
        self.case = kwargs["case"]
        self.solver = kwargs["solver"]

    def solve(self):
        raise NotImplementedError


class InitTask(Task):
    def solve(self):
        report = None
        try:
            report = self.solver.solve(self.case.get_cnf())
            self.case.mark_solved(report)
            self.case.check_solution()
        except Exception as e:
            rc.debugger.write(0, 2, "error while solving init case:\n%s" % e)

        return report


class MainTask(Task):
    def solve(self):
        try:
            report = self.solver.solve(self.case.get_cnf())
            self.case.mark_solved(report)
        except Exception as e:
            rc.debugger.write(0, 2, "error while solving main case:\n%s" % e)

        return self.case.get_status(short=True), self.case.time
