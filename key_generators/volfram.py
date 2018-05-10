import numpy as np

from key_generator import KeyGenerator


class Volfram(KeyGenerator):
    key_stream_start = 12417
    key_stream_len = 128

    secret_key_start = 1
    secret_key_len = 128

    name = "Volfram"

    def __init__(self, cnf):
        KeyGenerator.__init__(self, cnf)

    def set_secret_key(self, key, mask=np.ones(secret_key_len)):
        KeyGenerator.set_secret_key(self, key, mask)

    def __copy__(self):
        copy_volfram = Volfram(self.cnf)

        copy_volfram.substitution = self.substitution
        copy_volfram.key_stream = self.key_stream
        copy_volfram.secret_key = self.secret_key
        copy_volfram.secret_mask = self.secret_mask

        return copy_volfram
