import numpy as np

from key_generator import KeyGenerator


class Trivium_96(KeyGenerator):
    key_stream_start = 530
    key_stream_len = 100

    secret_key_start = 1
    secret_key_len = 96

    name = "Trivium 96"
    tag = "trivium_96"

    def __init__(self, cnf):
        KeyGenerator.__init__(self, cnf)

    def set_secret_key(self, key, mask=np.ones(secret_key_len)):
        KeyGenerator.set_secret_key(self, key, mask)

    def __copy__(self):
        copy_tr_96 = Trivium_96(self.cnf)

        copy_tr_96.substitution = self.substitution
        copy_tr_96.key_stream = self.key_stream
        copy_tr_96.secret_key = self.secret_key
        copy_tr_96.secret_mask = self.secret_mask

        return copy_tr_96
