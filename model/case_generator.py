from variable_set import KeyStream, PublicKey
from backdoor import SecretKey


class CaseGenerator:
    def __init__(self, **kwargs):
        self.algorithm = kwargs["algorithm"]
        self.random_state = kwargs["random_state"]

        self.secret_key = SecretKey(self.algorithm)
        self.key_stream = KeyStream(self.algorithm)
        self.public_key = PublicKey(self.algorithm) if hasattr(self.algorithm, 'public_key_len') else None

    def get_init_substitutions(self):
        init_substitutions = {
            "secret_key": self.secret_key.generate_substitution(self.random_state)
        }

        if self.public_key is not None:
            init_substitutions["public_key"] = self.public_key.generate_substitution(self.random_state)

        return init_substitutions

    def get_substitutions(self, backdoor, solution, rnd=""):
        substitutions = {
            "key_stream": self.__substitution(self.key_stream, 's', solution, rnd),
            "backdoor": self.__substitution(backdoor, 'b', solution, rnd)
        }

        if self.public_key is not None:
            substitutions["public_key"] = self.__substitution(self.public_key, 'p', solution, rnd)

        return substitutions

    @staticmethod
    def generate(algorithm, cnf, substitutions):
        case = algorithm(cnf)
        case.substitute(**substitutions)
        return case

    def __substitution(self, o, c, solution, rnd):
        if c in rnd:
            return o.generate_substitution(self.random_state)
        else:
            return o.get_substitution(solution)
