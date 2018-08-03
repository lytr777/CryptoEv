from key_generators.key_generator import KeyGenerator


class BlockCipher(KeyGenerator):
    public_key_start = None
    public_key_len = None

    def __init__(self, cnf):
        KeyGenerator.__init__(self, cnf)
        self.public_key = None

    def set_public_key(self, key):
        if self.public_key_len != len(key):
            raise Exception("Public key must contain %d bits" % self.public_key_len)

        self.public_key = key

    def __substitute_public_key(self):
        for i in range(len(self.public_key)):
            self.substitution.substitute(self.public_key_start + i, not self.public_key[i])

    def get_cnf(self):
        if self.public_key is not None:
            self.__substitute_public_key()

        return KeyGenerator.get_cnf(self)

    def get_solution_public_key(self):
        start = self.public_key_start - 1
        end = start + self.public_key_len
        return self.__get_key(start, end)
