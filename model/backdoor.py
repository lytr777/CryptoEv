import numpy as np
from copy import copy

from model.cnf_model import CnfSubstitution
from model.variable_set import VariableSet


class InextensibleBackdoor(VariableSet):
    def __init__(self, variables):
        VariableSet.__init__(self, variables)
        self.length = len(self.vars)
        self.mask = np.ones(self.length, dtype=np.int)

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
                raise Exception("Backdoor intersect with key stream")

            if pk_st <= var <= pk_end:
                raise Exception("Backdoor intersect with public key")

    def to_str(self, mask):
        if len(mask) != self.length:
            raise Exception("Mask length don't equals %d" % self.length)

        s = "["
        for i in range(self.length):
            if mask[i]:
                s += "%s " % self.vars[i]
        s = "%s](%d)" % (s[:-1], np.count_nonzero(mask))
        return s

    def __str__(self):
        return self.to_str(self.mask)

    def __len__(self):
        return np.count_nonzero(self.mask)

    def get(self):
        return copy(self.mask)

    def set(self, mask):
        if len(mask) != self.length:
            raise Exception("Mask length don't equals %d" % self.length)

        self.mask = copy(mask)

    def reset(self):
        self.mask = np.ones(self.length, dtype=np.int)

    def snapshot(self, mask=None):
        mask = self.mask if mask is None else mask
        variables = []
        for i in range(len(mask)):
            if mask[i]:
                variables.append(self.vars[i])

        return FixedBackdoor(variables)

    def get_substitution(self, solution):
        if len(solution) < self.max:
            raise Exception("Solution has too few variables: %d" % len(solution))

        substitution = CnfSubstitution()
        for i, var in enumerate(self.vars):
            if self.mask[i]:
                substitution.substitute(var, not solution[var - 1])

        return substitution

    def generate_substitution(self, random_state):
        substitution = CnfSubstitution()
        values = random_state.randint(2, size=self.length)
        for i, var in enumerate(self.vars):
            if self.mask[i]:
                substitution.substitute(var, not values[i])

        return substitution

    @staticmethod
    def load(path):
        with open(path, 'r') as f:
            variables = [int(var) for var in f.readline().split(' ')]
            return InextensibleBackdoor(variables)


class SecretKey(InextensibleBackdoor):
    def __init__(self, algorithm):
        st = algorithm.secret_key_start
        end = st + algorithm.secret_key_len
        InextensibleBackdoor.__init__(self, range(st, end))
        self.max_len = end - 1


class FixedBackdoor(VariableSet):
    def __init__(self, variables):
        VariableSet.__init__(self, variables)

    def __str__(self):
        s = "["
        for var in self.vars:
            s += "%s " % var
        s = s[:-1] + "](%d)" % self.__len__()
        return s

    @staticmethod
    def from_str(s):
        s = s.split('(')[0]
        variables = [int(var) for var in s[1:-1].split(' ')]

        return FixedBackdoor(variables)
