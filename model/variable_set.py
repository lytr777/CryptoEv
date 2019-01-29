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

    def get_values(self, solution):
        if len(solution) < self.max:
            raise Exception("Solution has too few variables: %d" % len(solution))

        values = []
        for var in self.vars:
            values.append(solution[var - 1])

        return values

    def set_values(self, solution, values):
        if len(solution) < self.max:
            raise Exception("Solution has too few variables: %d" % len(solution))

        for i, var in enumerate(self.vars):
            solution[var - 1] = values[i]

    def get_substitution(self, solution):
        if len(solution) < self.max:
            raise Exception("Solution has too few variables: %d" % len(solution))

        substitution = CnfSubstitution()
        for var in self.vars:
            var = var if solution[var - 1] else -var
            substitution.substitute(var)

        return substitution

    def generate_substitution(self, random_state):
        substitution = CnfSubstitution()
        values = random_state.randint(2, size=self.__len__())
        for i, var in enumerate(self.vars):
            var = var if values[i] else -var
            substitution.substitute(var)

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
