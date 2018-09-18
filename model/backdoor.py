import numpy as np
from copy import copy

from model.cnf_model import CnfSubstitution
from model.variable_set import VariableSet
from algorithm.module.mutation import scaled_uniform_mutation


class Backdoor(VariableSet):
    # overridden methods
    def __init__(self, variables):
        VariableSet.__init__(self, variables)
        self.length = len(self.vars)
        self.mask = np.ones(self.length, dtype=np.int)

    def __str__(self):
        s = "["
        for i in range(self.length):
            if self.mask[i]:
                s += "%s " % self.vars[i]
        s = "%s](%d)" % (s[:-1], np.count_nonzero(self.mask))
        return s

    def __len__(self):
        return np.count_nonzero(self.mask)

    def __copy__(self):
        return self.get_copy(self.mask)

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

    # support methods
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

    def snapshot(self):
        variables = []
        for i in range(len(self.mask)):
            if self.mask[i]:
                variables.append(self.vars[i])

        return FixedBackdoor(variables)

    def pack(self):
        array = np.empty(2 * self.length, dtype=np.int)
        array[:self.length] = np.array(self.vars)
        array[self.length:] = self.mask

        return array

    @staticmethod
    def unpack(array):
        lenght = len(array) / 2
        backdoor = Backdoor(array[:lenght])
        backdoor.__set_mask(array[lenght:])

        return backdoor

    @staticmethod
    def load(path):
        with open(path, 'r') as f:
            variables = [int(var) for var in f.readline().split(' ')]
            return Backdoor(variables)

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
        self.__set_mask(np.ones(self.length, dtype=np.int))

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
            if self.mask[pos] == 0:
                self.mask[pos] = 1
            else:
                raise Exception("Variable %d already exists in backdoor" % var)
        else:
            self.vars.insert(pos, var)

            self.length += 1
            self.max = self.vars[-1]

            new_mask = np.ones(self.length, dtype=np.int)
            for i in range(self.length):
                if i < pos:
                    new_mask[i] = self.mask[i]
                elif i > pos:
                    new_mask[i] = self.mask[i - 1]
            self.mask = new_mask


class SecretKey(Backdoor):
    def __init__(self, algorithm):
        st = algorithm.secret_key_start
        end = st + algorithm.secret_key_len
        Backdoor.__init__(self, range(st, end))


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


if __name__ == "__main__":
    mutation_f = scaled_uniform_mutation(1.)
    bd = Backdoor([1, 3, 4, 5, 6])
    print bd

    bd = bd.get_copy(np.array([1, 0, 0, 1, 1]))
    print bd

    print bd.find(4)

    bd.add(2)
    print bd

    print bd.find(4)

    bd = Backdoor.unpack(np.array([1, 2, 3, 4, 5, 6, 0, 0, 1, 1, 0, 1]))
    print bd.pack()
