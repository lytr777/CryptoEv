import os

from util.constant import solver_paths


class Wrapper:
    def __init__(self, info, tl_util):
        self.info = info
        self.tl_util = tl_util
        self.solver_path = solver_paths[self.info["tag"]]

    def check_installation(self):
        if not os.path.isdir(self.info["dir"]) or not os.path.exists(self.solver_path):
            args = (self.info["tag"], self.info["script"])
            raise Exception("SAT-solver %s is not installed. Try to run %s script." % args)

    def get_arguments(self, tl=None, workers=None, simplifying=True):
        if self.tl_util:
            tl = 1 if tl is None else tl
            return self.get_timelimit_arguments(tl, workers, simplifying)
        else:
            return self.get_common_arguments(tl, workers, simplifying)

    def get_common_arguments(self, tl, workers, simplifying):
        raise NotImplementedError

    def get_timelimit_arguments(self, tl, workers, simplifying):
        raise NotImplementedError

    def parse_out(self, output):
        raise NotImplementedError
