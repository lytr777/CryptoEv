import numpy as np
from copy import copy

from key_generator import KeyGenerator


class A5_toy(KeyGenerator):
    key_stream_start = 3931
    key_stream_len = 80

    secret_key_start = 1
    secret_key_len = 48

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
        copy_a5_toy = A5_toy(self.cnf_link)

        copy_a5_toy.key_stream = self.key_stream
        copy_a5_toy.secret_key = self.secret_key
        copy_a5_toy.secret_mask = self.secret_mask

        return copy_a5_toy
