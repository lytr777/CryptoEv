from rokk import options as rokk_options
import numpy as np

from constants.runtime import runtime_constants as rc

options_map = {
    'rokk': rokk_options
}


class Option:
    def __init__(self, option):
        self.option = option
        self.type = option['type']
        self.value = option['default']

    def __str__(self):
        if self.type == 'bool':
            return self.option[self.value]
        else:
            return '%s=%s' % (self.option['param'], self.value)

    def rnd(self):
        if self.type == 'bool':
            self.value = bool(np.random.randint(2, size=1))
        elif self.type == 'int32':
            mn = self.option['min']
            mx = self.option['max'] if self.option['max'] != 'imax' else 2147483647
            self.value = mn + np.random.randint(mx - mn)
        elif self.type == 'double':
            mn = self.option['min']
            mx = self.option['max'] if self.option['max'] != 'inf' else 9223372036854775807
            self.value = mn + (np.random.rand() * (mx - mn))


class SolverOptions:
    def __init__(self, name):
        try:
            self.options = options_map[name]
        except KeyError as e:
            self.options = []

        self.s = None
        self.params = []
        for option in self.options:
            self.params.append(Option(option))

    def get(self):
        if self.s is None:
            return map(str, self.params)
        else:
            return self.s.split(' ')

    def rnd(self):
        if self.s is None:
            for param in self.params:
                param.rnd()
        else:
            rc.debugger.write(1, 2, "Try to change solver option in nonroot node!!!")

    def set(self, s):
        self.s = s

    def __str__(self):
        if self.s is None:
            return ' '.join(self.get())
        else:
            return self.s


if __name__ == '__main__':
    sp = SolverOptions('rokk')
    print str(sp)
