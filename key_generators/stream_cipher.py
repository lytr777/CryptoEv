from key_generators.key_generator import KeyGenerator


class StreamCipher(KeyGenerator):
    def __init__(self, cnf):
        KeyGenerator.__init__(self, cnf)
