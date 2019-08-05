import os
import re
import subprocess
import threading

from time import time as now

from solver_net import SolverSettings
from constants.static import solver_paths
from errors.tracer import trace_solver_error
from model.solver_report import SolverReport
from options.solver_options import SolverOptions
from constants.runtime import runtime_constants as rc


class Solver:
    name = "solver"

    def __init__(self, info, **kwargs):
        self.dir = info["dir"]
        self.name = info["name"]
        self.script = info["script"]

        self.tag = kwargs["tag"]
        self.solver_path = solver_paths[self.name]
        self.spaces = re.compile('[\t ]+')

        self.sett = SolverSettings(**kwargs)
        self.options = SolverOptions(self.name)

    def check_installation(self):
        if not os.path.isdir(self.dir) or not os.path.exists(self.solver_path):
            args = (self.name, self.script)
            raise Exception("SAT-solver %s is not installed. Try to run %s script." % args)

    def get_params(self):
        return self.options

    def set_params(self, options):
        self.options = options

    def reset_params(self):
        self.options = SolverOptions(self.name)

    def solve(self, cnf):
        g = self.sett.get

        args, tl = [], g("tl")
        if g("tl_util"):
            args.extend(["timelimit", "-t%d" % max(1, tl)])
            tl = 0
        l_args = self.get_arguments(args, g("workers"), tl, g("simplify"))
        if self.tag != 'init':
            l_args.extend(self.options.get())
        thread_name = threading.current_thread().name

        report = None
        for i in range(g("attempts")):
            if report is None or report.check():
                rc.debugger.write(3, 2, "%s start solving %s case" % (thread_name, self.tag))
                st = now()
                sp = subprocess.Popen(l_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, err = sp.communicate(cnf)
                time = now() - st
                if len(err) != 0 and not err.startswith('timelimit'):
                    rc.debugger.write(1, 2, "%s didn't solve %s case:\n%s" % (thread_name, self.tag, err))
                    trace_solver_error(thread_name, "Subprocess error", '-', output, err)

                try:
                    report = self.parse_out(output)
                    if report.status == "INDETERMINATE":
                        report.time = time
                except KeyError as e:
                    rc.debugger.write(1, 2, "%s error while parsing %s case" % (thread_name, self.tag))
                    report = SolverReport("INDETERMINATE", time)

                    if len(output) > 0:
                        title = "Key error while parsing output"
                        trace_solver_error(thread_name, title, '-', output, "%s\n\n%s" % (err, e))

                rc.debugger.write(3, 2, "%s solved %s case with status: %s" % (thread_name, self.tag, report.status))
                if report.check():
                    title = "Error while parsing solution"
                    trace_solver_error(thread_name, title, '-', output, "%s in %d attempt" % (report.status, i))

        if report.check():
            report = SolverReport("INDETERMINATE", g("tl"))

        return report

    def get_arguments(self, args, workers, tl, simp):
        raise NotImplementedError

    def parse_out(self, output):
        raise NotImplementedError

    def __check_code(self, rc):
        if rc == 0 or rc == 10 or rc == 20:  # standard exit
            return False
        # if rc == 143:  # timelimit exit
        #     return False
        return True

    def __str__(self):
        return self.name
