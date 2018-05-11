import numpy as np

from key_generator import KeyGenerator


class Geffe(KeyGenerator):
    key_stream_start = 301
    key_stream_len = 100

    secret_key_start = 1
    secret_key_len = 64

    name = "Geffe"

    def __init__(self, cnf):
        KeyGenerator.__init__(self, cnf)

    def set_secret_key(self, key, mask=np.ones(secret_key_len)):
        KeyGenerator.set_secret_key(self, key, mask)

    def __copy__(self):
        copy_geffe = Geffe(self.cnf)

        copy_geffe.substitution = self.substitution
        copy_geffe.key_stream = self.key_stream
        copy_geffe.secret_key = self.secret_key
        copy_geffe.secret_mask = self.secret_mask

        return copy_geffe
