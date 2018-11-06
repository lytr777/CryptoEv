import os
import re
import subprocess
import threading

from time import time as now
from solver_net import SolverSettings
from constants.static import solver_paths
from model.solver_report import SolverReport
from constants.runtime import runtime_constants as rc


class Solver:
    name = "solver"

    def __init__(self, info, **kwargs):
        self.tag = kwargs["tag"]
        self.info = info
        self.solver_path = solver_paths[self.info["name"]]
        self.name = self.info["name"]
        self.spaces = re.compile('[\t ]+')

        self.sett = SolverSettings(**kwargs)

    def check_installation(self):
        if not os.path.isdir(self.info["dir"]) or not os.path.exists(self.solver_path):
            args = (self.info["name"], self.info["script"])
            raise Exception("SAT-solver %s is not installed. Try to run %s script." % args)

    def solve(self, cnf):
        g = self.sett.get

        args, tl = [], g("tl")
        if g("tl_util"):
            args.extend(["timelimit", "-t%d" % max(1, tl)])
            tl = 0
        l_args = self.get_arguments(args, g("workers"), tl, g("simplify"))
        thread_name = threading.current_thread().name

        report = None
        for i in range(g("attempts")):
            if report is None or report.check():
                rc.debugger.write(3, 2, "%s start solving %s case" % (thread_name, self.tag))
                st = now()
                sp = subprocess.Popen(l_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, err = sp.communicate(cnf)
                time = now() - st
                if len(err) != 0 and self.__check_code(sp.returncode):
                    rc.debugger.write(1, 2, "%s didn't solve %s case:\n%s" % (thread_name, self.tag, err))
                    raise Exception(err)

                try:
                    report = self.parse_out(output)
                    if report.status == "INDETERMINATE":
                        report.time = time
                except KeyError:
                    rc.debugger.write(1, 2, "%s error while parsing %s case" % (thread_name, self.tag))
                    report = SolverReport("INDETERMINATE", time)
                rc.debugger.write(3, 2, "%s solved %s case with status: %s" % (thread_name, self.tag, report.status))

        if report.check():
            raise Exception("All %d times main case hasn't been solved" % g("attempts"))

        return report

    def get_arguments(self, args, workers, tl, simp):
        raise NotImplementedError

    def parse_out(self, output):
        raise NotImplementedError

    def __check_code(self, rc):
        if rc == 0 or rc == 10 or rc == 20:  # standard exit
            return False
        if rc == 143:  # timelimit exit
            return False
        return True

    def __str__(self):
        return self.name
