import subprocess
import tempfile

import os


class CaseSolver:
    def __init__(self, solver_wrapper):
        self.solver_wrapper = solver_wrapper

    def start(self, args, case):
        time_limit = args["time_limit"] if ("time_limit" in args) else None

        cnf_file = tempfile.NamedTemporaryFile(prefix="cnf").name
        out_file = tempfile.NamedTemporaryFile(prefix="out").name
        launching_args = self.solver_wrapper.get_arguments(cnf_file, out_file, time_limit=time_limit)

        case.write_to(cnf_file)

        p = subprocess.Popen(launching_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.communicate()[0]  # bugs with plingeling

        time, status = self.solver_wrapper.parse_out(out_file, output)

        case.mark_solved(time, status, out_file)

        os.remove(cnf_file)
        os.remove(out_file)
