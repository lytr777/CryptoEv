from key_generators.key_generator import KeyGenerator


class BlockCipher(KeyGenerator):
    public_key_start = None
    public_key_len = None

    def __init__(self, cnf):
        KeyGenerator.__init__(self, cnf)
        self.public_key = None
