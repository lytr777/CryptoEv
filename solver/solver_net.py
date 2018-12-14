class SolverSettings:
    def __init__(self, **kwargs):
        self.settings = {
            "tl_util": False,
            "tl": 0,
            "workers": 1,
            "attempts": 5,
            "simplify": True
        }

        self.update(**kwargs)

    def update(self, **kwargs):
        for key in kwargs.keys():
            if key in self.settings:
                self.settings[key] = kwargs[key]

    def get(self, key):
        return self.settings[key]

    def __str__(self):
        return self.settings.__str__()


class SolverNet:
    def __init__(self, **kwargs):
        self.solvers = {}

        for key in kwargs.keys():
            if key.__contains__("solver"):
                value = kwargs[key]
                self.solvers[value.tag] = value

    def solve(self, tag, cnf):
        return self.solvers[tag].solve(cnf)

    # getters
    def __get_sett(self, tag):
        return self.solvers[tag].sett

    def get(self, tag):
        return self.solvers[tag]

    def get_param(self, tag, key):
        return self.__get_sett(tag).get(key)

    def get_tl(self, tag):
        return self.get_param(tag, "tl")

    def get_workers(self, tag):
        return self.get_param(tag, "workers")

    def get_attempts(self, tag):
        return self.get_param(tag, "attempts")

    def get_simplify(self, tag):
        return self.get_param(tag, "simplify")

    def get_debugger(self, tag):
        return self.get_param(tag, "debugger")

    # setters
    def set_params(self, tag, **kwargs):
        self.__get_sett(tag).update(**kwargs)

    def set_tl(self, tag, value):
        self.set_params(tag, tl=value)

    def set_workers(self, tag, value):
        self.set_params(tag, worker=value)

    def set_attempts(self, tag, value):
        self.set_params(tag, attempts=value)

    def set_simplify(self, tag, value):
        self.set_params(tag, simplify=value)

    def set_debugger(self, tag, obj):
        self.set_params(tag, debugger=obj)

    def __iter__(self):
        for solver in self.solvers.values():
            yield solver

    def __str__(self):
        s = ', '.join(['%s(%s)' % (v, k) for k, v in self.solvers.items()])
        return "solvers: %s" % s
