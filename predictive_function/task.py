from constants import static
from constants.runtime import runtime_constants as rc
from model.case_generator import CaseGenerator
from util.parse.cnf_parser import CnfParser


class Task:
    def __init__(self, **kwargs):
        self.substitutions = kwargs["substitutions"]
        self.algorithm = kwargs["algorithm"]
        self.solver = kwargs["solver"]

    def solve(self):
        raise NotImplementedError


class InitTask(Task):
    def solve(self):
        if rc.cnf is None:
            print "parsing cnf..."
            cnf_path = static.cnfs[self.algorithm.tag]
            rc.cnf = CnfParser().parse_for_path(cnf_path)

        case = CaseGenerator.generate(self.algorithm, rc.cnf, self.substitutions)
        report = None
        try:
            report = self.solver.solve(case.get_cnf())
            case.mark_solved(report)
            case.check_solution()
        except Exception as e:
            rc.debugger.write(0, 2, "error while solving init case:\n%s" % e)

        return report


class MainTask(Task):
    def solve(self):
        if rc.cnf is None:
            print "parsing cnf..."
            cnf_path = static.cnfs[self.algorithm.tag]
            rc.cnf = CnfParser().parse_for_path(cnf_path)

        case = CaseGenerator.generate(self.algorithm, rc.cnf, self.substitutions)
        try:
            report = self.solver.solve(case.get_cnf())
            case.mark_solved(report)
        except Exception as e:
            rc.debugger.write(0, 2, "error while solving main case:\n%s" % e)

        return case.get_status(short=True), case.time
