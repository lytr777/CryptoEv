from copy import copy
import numpy as np

from key_generator import KeyGenerator


class Trivium_64(KeyGenerator):
    key_stream_start = 398
    key_stream_len = 75

    secret_key_start = 1
    secret_key_len = 64

    name = "Trivium 64"

    def __init__(self, cnf):
        self.cnf_link = cnf
        KeyGenerator.__init__(self)

    def set_secret_key(self, key, mask=np.ones(secret_key_len)):
        KeyGenerator.set_secret_key(self, key, mask)

    def write_to(self, file_path):
        self.cnf = copy(self.cnf_link)
        KeyGenerator.write_to(self, file_path)

    def get_cnf(self):
        self.cnf = copy(self.cnf_link)
        return KeyGenerator.get_cnf(self)

    def __copy__(self):
        copy_tr_64 = Trivium_64(self.cnf_link)

        copy_tr_64.key_stream = self.key_stream
        copy_tr_64.secret_key = self.secret_key
        copy_tr_64.secret_mask = self.secret_mask

        return copy_tr_64
