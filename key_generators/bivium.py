import numpy as np
from copy import copy

from key_generator import KeyGenerator


class Bivium(KeyGenerator):
    key_stream_start = 443
    key_stream_len = 200

    secret_key_start = 1
    secret_key_len = 177

    def __init__(self, cnf):
        self.cnf_link = cnf
        KeyGenerator.__init__(self)

    def set_secret_key(self, key, mask=np.ones(secret_key_len)):
        KeyGenerator.set_secret_key(self, key, mask)

    def write_to(self, file_path):
        self.cnf = copy(self.cnf_link)
        KeyGenerator.write_to(self, file_path)

    def __copy__(self):
        copy_bivium = Bivium(self.cnf_link)

        copy_bivium.key_stream = self.key_stream
        copy_bivium.secret_key = self.secret_key
        copy_bivium.secret_mask = self.secret_mask

        return copy_bivium
