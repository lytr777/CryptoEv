import numpy as np
from copy import copy

from algorithm.key_generator import KeyGenerator


class A5_1(KeyGenerator):
    key_stream_start = 8298
    key_stream_len = 128

    secret_key_start = 1
    secret_key_len = 64

    def __init__(self, cnf):
        self.cnf_link = cnf
        KeyGenerator.__init__(self)

    def set_secret_key(self, key, mask=np.ones(secret_key_len)):
        KeyGenerator.set_secret_key(self, key, mask)

    def write_to(self, file_path):
        self.cnf = copy(self.cnf_link)
        KeyGenerator.write_to(self, file_path)

    def __copy__(self):
        copy_a5_1 = A5_1(self.cnf_link)

        copy_a5_1.key_stream = self.key_stream
        copy_a5_1.secret_key = self.secret_key
        copy_a5_1.secret_mask = self.secret_mask

        return copy_a5_1
