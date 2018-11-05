from variable_set import KeyStream, PublicKey
from backdoor import SecretKey


class CaseGenerator:
    def __init__(self, algorithm, cnf, random_state):
        self.algorithm = algorithm
        self.cnf = cnf
        self.random_state = random_state

        self.secret_key = SecretKey(algorithm)
        self.key_stream = KeyStream(algorithm)
        self.public_key = PublicKey(algorithm) if hasattr(algorithm, 'public_key_len') else None

    def generate_init(self):
        case = self.algorithm(self.cnf)

        sk_substitution = self.secret_key.generate_substitution(self.random_state)
        case.add_substitution("secret_key", sk_substitution)

        if self.public_key is not None:
            pk_substitution = self.public_key.generate_substitution(self.random_state)
            case.add_substitution("public_key", pk_substitution)

        return case

    def generate(self, backdoor, solution, rnd=""):
        case = self.algorithm(self.cnf)

        if self.public_key is not None:
            pk_substitution = self.__substitution(self.public_key, 'p', solution, rnd)
            case.add_substitution("public_key", pk_substitution)

        bd_substitution = self.__substitution(backdoor, 'b', solution, rnd)
        case.add_substitution("backdoor", bd_substitution)

        ks_substitution = self.__substitution(self.key_stream, 's', solution, rnd)
        case.add_substitution("key_stream", ks_substitution)

        return case

    def __substitution(self, o, c, solution, rnd):
        if rnd.__contains__(c):
            return o.generate_substitution(self.random_state)
        else:
            return o.get_substitution(solution)
