import numpy as np
from copy import copy

from key_generator import KeyGenerator


class E0(KeyGenerator):
    key_stream_start = 1785
    key_stream_len = 128

    secret_key_start = 1
    secret_key_len = 128

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
        copy_e0 = E0(self.cnf_link)

        copy_e0.key_stream = self.key_stream
        copy_e0.secret_key = self.secret_key
        copy_e0.secret_mask = self.secret_mask

        return copy_e0