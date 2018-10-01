import warnings

from model.cnf import CnfSubstitution


class VariableSet:
    def __init__(self, variables):
        self.vars = sorted(list(set(variables)))
        self.min = self.vars[0]
        self.max = self.vars[-1]

        if len(variables) != len(self.vars):
            warnings.warn("Repeating variables in list", Warning)

        if self.min <= 0:
            raise Exception("Negative numbers or zero in variable set")

    def __len__(self):
        return len(self.vars)

    def __str__(self):
        return str(self.vars)

    def get_substitution(self, solution):
        if len(solution) < self.max:
            raise Exception("Solution has too few variables: %d" % len(solution))

        substitution = CnfSubstitution()
        for number in self.vars:
            substitution.substitute(number, not solution[number - 1])

        return substitution

    def generate_substitution(self, random_state):
        substitution = CnfSubstitution()
        values = random_state.randint(2, size=self.__len__())
        for i, var in enumerate(self.vars):
            substitution.substitute(var, not values[i])

        return substitution


class KeyStream(VariableSet):
    def __init__(self, algorithm):
        st = algorithm.key_stream_start
        end = st + algorithm.key_stream_len
        VariableSet.__init__(self, range(st, end))


class PublicKey(VariableSet):
    def __init__(self, algorithm):
        if not hasattr(algorithm, 'public_key_len'):
            raise Exception("%s doesn't have a public key" % algorithm.name)

        st = algorithm.public_key_start
        end = st + algorithm.public_key_len
        VariableSet.__init__(self, range(st, end))
