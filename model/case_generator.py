from variable_set import KeyStream, PublicKey
from backdoor import SecretKey


class CaseGenerator:
    def __init__(self, algorithm, cnf, random_state, backdoor):
        self.algorithm = algorithm
        self.cnf = cnf
        self.random_state = random_state

        self.secret_key = SecretKey(algorithm)
        self.key_stream = KeyStream(algorithm)
        self.public_key = PublicKey(algorithm) if hasattr(algorithm, 'public_key_len') else None

        self.backdoor = backdoor

    def generate_init(self):
        case = self.algorithm(self.cnf)

        sk_substitution = self.secret_key.generate_substitution(self.random_state)
        case.add_substitution("secret_key", sk_substitution)

        if self.public_key is not None:
            pk_substitution = self.public_key.generate_substitution(self.random_state)
            case.add_substitution("public_key", pk_substitution)

        return case

    def generate(self, solution):
        if self.backdoor is None:
            raise Exception("Backdoor not specified")

        case = self.algorithm(self.cnf)

        if self.public_key is not None:
            pk_substitution = self.public_key.get_substitution(solution)
            case.add_substitution("public_key", pk_substitution)

        bd_substitution = self.backdoor.get_substitution(solution)
        case.add_substitution("backdoor", bd_substitution)

        ks_substitution = self.key_stream.get_substitution(solution)
        case.add_substitution("key_stream", ks_substitution)

        return case
