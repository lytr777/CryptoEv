import os

from util.constant import solver_paths


class Wrapper:
    def __init__(self, info):
        self.info = info
        self.solver_path = solver_paths[self.info["tag"]]

    def check_installation(self):
        if not os.path.isdir(self.info["dir"]) or not os.path.exists(self.solver_path):
            args = (self.info["tag"], self.info["script"])
            raise Exception("SAT-solver %s is not installed. Try to run %s script." % args)

    def get_arguments(self, tl, workers, simplifying):
        raise NotImplementedError

    def parse_out(self, output):
        raise NotImplementedError
