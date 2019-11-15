import numpy as np
from copy import copy

from model.cnf import CnfSubstitution
from model.variable_set import VariableSet
from algorithm.module.mutation import UniformMutation


def build_intervals(variables):
    intervals = []
    interval = [variables[0], variables[0]]

    for i in range(1, len(variables)):
        if variables[i] - interval[1] == 1:
            interval[1] = variables[i]
        else:
            intervals.append(interval)
            interval = [variables[i], variables[i]]
    intervals.append(interval)
    return intervals


class Backdoor(VariableSet):
    # overridden methods
    def __init__(self, variables):
        VariableSet.__init__(self, variables)
        self.length = len(self.vars)
        self.mask = [True] * self.length

    def __str__(self):
        if len(self) == 0:
            return '[]'
        intervals = build_intervals(self.__variables())

        s = '['
        for il in intervals:
            if il[1] - il[0] > 2:
                s += '%s..%s ' % (il[0], il[1])
            else:
                ss = ' '.join(str(x) for x in range(il[0], il[1] + 1))
                s += '%s ' % ss
        s = s[:-1] + '](%d)' % len(self)
        return s

    def __len__(self):
        return np.count_nonzero(self.mask)

    def __copy__(self):
        return self.get_copy(self.mask)

    def __iter__(self):
        for i in range(self.length):
            if self.mask[i]:
                yield self.vars[i]

    def get_values(self, solution):
        if len(solution) < self.max:
            raise Exception("Solution has too few variables: %d" % len(solution))

        values = []
        for i, var in enumerate(self.vars):
            if self.mask[i]:
                values.append(solution[var - 1])

        return values

    def set_values(self, solution, values):
        if len(solution) < self.max:
            raise Exception("Solution has too few variables: %d" % len(solution))

        j = 0
        for i, var in enumerate(self.vars):
            if self.mask[i]:
                solution[var - 1] = values[j]
                j += 1

        assert j == len(values)

    def get_substitution(self, solution):
        if len(solution) < self.max:
            raise Exception("Solution has too few variables: %d" % len(solution))

        substitution = CnfSubstitution()
        for i, var in enumerate(self.vars):
            if self.mask[i]:
                var = var if solution[var - 1] else -var
                substitution.substitute(var)

        return substitution

    def generate_substitution(self, random_state):
        substitution = CnfSubstitution()
        values = random_state.randint(2, size=self.__len__())
        j = 0
        for i, var in enumerate(self.vars):
            if self.mask[i]:
                var = var if values[j] else -var
                substitution.substitute(var)
                j += 1

        assert j == len(values)

        return substitution

    # support methods
    def __variables(self):
        variables = []
        for i in range(len(self.mask)):
            if self.mask[i]:
                variables.append(self.vars[i])

        return variables

    def check(self, algorithm):
        ks_st = algorithm.key_stream_start
        ks_end = ks_st + algorithm.key_stream_len - 1
        if hasattr(algorithm, 'public_key_len'):
            pk_st = algorithm.public_key_start
            pk_end = pk_st + algorithm.public_key_len - 1
        else:
            pk_st, pk_end = 0, 0

        for var in self.vars:
            if ks_st <= var <= ks_end:
                rng = "%d <= %d <= %d" % (ks_st, var, ks_end)
                raise Exception("Backdoor intersect with key stream: %s" % rng)

            if pk_st <= var <= pk_end:
                rng = "%d <= %d <= %d" % (pk_st, var, pk_end)
                raise Exception("Backdoor intersect with public key: %s" % rng)

    def snapshot(self):
        return FixedBackdoor(self.__variables())

    def pack(self):
        array = copy(self.vars)
        array.extend(self.mask)

        return array

    @staticmethod
    def unpack(array):
        lenght = len(array) / 2
        backdoor = Backdoor(array[:lenght])
        backdoor.__set_mask(array[lenght:])

        return backdoor

    @staticmethod
    def load(path):
        with open(path) as f:
            lines = f.readlines()
            backdoors = []
            for line in lines:
                if len(line) > 0:
                    line = line[:-1] if line[-1] == '\n' else line
                    variables = [int(var) for var in line.split(' ')]
                    backdoors.append(Backdoor(variables))

            return backdoors

    # mask
    def __set_mask(self, mask):
        if len(mask) != self.length:
            raise Exception("Mask length don't equals %d" % self.length)

        self.mask = copy(mask)

    def get_mask(self):
        return copy(self.mask)

    def get_copy(self, mask):
        bd = Backdoor(self.vars)
        bd.__set_mask(mask)
        return bd

    def reset(self):
        self.__set_mask([True] * self.length)

    def find(self, var, insert=False):
        l, r = 0, len(self.vars)
        while r - l > 1:
            c = int((l + r) / 2)
            if self.vars[c] > var:
                r = c
            else:
                l = c

        if self.vars[l] == var:
            return l

        if insert:
            return l if self.vars[l] > var else r

        return -1

    def add(self, var):
        pos = self.find(var, insert=True)

        if len(self.vars) > pos and self.vars[pos] == var:
            if not self.mask[pos]:
                self.mask[pos] = True
            else:
                raise Exception("Variable %d already exists in backdoor" % var)
        else:
            self.vars.insert(pos, var)
            self.mask.insert(pos, True)

            self.length += 1
            self.max = self.vars[-1]


class SecretKey(Backdoor):
    def __init__(self, algorithm):
        st = algorithm.secret_key_start
        end = st + algorithm.secret_key_len
        Backdoor.__init__(self, range(st, end))


class FixedBackdoor(VariableSet):
    def __init__(self, variables):
        VariableSet.__init__(self, variables)

    def __str__(self):
        intervals = build_intervals(self.vars)

        s = '['
        for il in intervals:
            if il[1] - il[0] > 2:
                s += '%s..%s ' % (il[0], il[1])
            else:
                ss = ' '.join(str(x) for x in range(il[0], il[1] + 1))
                s += '%s ' % ss
        s = s[:-1] + '](%d)' % self.__len__()
        return s

    @staticmethod
    def from_str(s):
        s = s.split('(')[0]
        variables = []
        for lit in s[1:-1].split(' '):
            if '.' in lit:
                var = lit.split('..')
                variables.extend(range(int(var[0]), int(var[1]) + 1))
            else:
                variables.append(int(lit))
        # variables = [int(var) for var in s[1:-1].split(' ')]

        return FixedBackdoor(variables)

    def to_str(self):
        s = ' '.join(str(v) for v in self.vars)
        return "[%s](%d)" % (s, len(self))

    def snapshot(self):
        return self


if __name__ == "__main__":
    mutation = UniformMutation(scale=1.)
    bd = Backdoor([1, 2, 3, 4, 5, 6])
    print bd

    bds = bd.snapshot()
    print bds

    bd = bd.get_copy([1, 0, 0, 0, 1, 1])
    print bd

    bd = mutation.mutate(bd)
    print bd

    # print bd.find(4)
    #
    # bd.add(2)
    # print bd
    #
    # print bd.find(4)
    #
    # bd = Backdoor.unpack([1, 2, 3, 4, 5, 6, 0, 0, 1, 1, 0, 1])
    # print bd.pack()
