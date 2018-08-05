import warnings
from copy import copy

from model.backdoor_list import BackdoorList
from model.cnf_model import CnfSubstitution


class VariableSet:
    def __init__(self, variables):
        self.vars = set(variables)
        self.max_len = max(self.vars)

        if len(variables) != len(self.vars):
            warnings.warn("Repeating variables in list", Warning)

        if min(self.vars) <= 0:
            raise Exception("Negative numbers or zero in variable set")

    def __len__(self):
        return len(self.vars)

    def __str__(self):
        return str(self.vars)

    def get_substitution(self, solution):
        if len(solution) < self.max_len:
            raise Exception("Solution has too few variables: %d" % len(solution))

        substitution = CnfSubstitution()
        for number in self.vars:
            substitution.substitute(number, not solution[number - 1])

        return substitution

    def generate_substitution(self, random_state):
        substitution = CnfSubstitution()
        values = random_state.randint(2, size=self.__len__())
        for i, number in enumerate(self.vars):
            substitution.substitute(number, values[i])

        return substitution


class Backdoor(VariableSet):
    def __init__(self, algorithm, variables):
        VariableSet.__init__(self, variables)
        self.max_len = algorithm.key_stream_start - 1
        self.backdoor_list = BackdoorList(self.vars)

        if len(self.vars) > self.max_len:
            raise Exception("Backdoor has too many variables")

        if max(self.vars) > self.max_len:
            raise Exception("Backdoor out of bounds")

    def __str__(self):
        return self.backdoor_list.get_key()

    def to_list(self):
        return copy(self.backdoor_list)

    def from_list(self, new_list):
        if self.backdoor_list.var_list != new_list.var_list:
            raise Exception("")

        for i in range(len(new_list)):
            if new_list[i] != self.backdoor_list[i]:
                if new_list.get_var(i) in self.vars:
                    self.vars.remove(new_list.get_var(i))
                else:
                    self.vars.add(new_list.get_var(i))

        self.backdoor_list = new_list

    @staticmethod
    def load(path, algorithm):
        with open(path, 'r') as f:
            variables = [int(var) for var in f.readline().split(' ')]
            return Backdoor(algorithm, variables)


class KeyStream(VariableSet):
    def __init__(self, algorithm):
        st = algorithm.key_stream_start
        end = st + algorithm.key_stream_len
        VariableSet.__init__(self, range(st, end))
        self.max_len = end - 1


class PublicKey(VariableSet):
    def __init__(self, algorithm):
        if not hasattr(algorithm, 'public_key_len'):
            raise Exception("%s doesn't have a public key" % algorithm.name)

        st = algorithm.public_key_start
        end = st + algorithm.public_key_len
        VariableSet.__init__(self, range(st, end))
        self.max_len = end - 1


class SecretKey(Backdoor):
    def __init__(self, algorithm):
        st = algorithm.secret_key_start
        end = st + algorithm.secret_key_len
        Backdoor.__init__(self, algorithm, range(st, end))
        self.max_len = end - 1
