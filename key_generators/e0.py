import numpy as np

from stream_cipher import StreamCipher


class E0(StreamCipher):
    key_stream_start = 1785
    key_stream_len = 128

    secret_key_start = 1
    secret_key_len = 128

    name = "E0"
    tag = "e0"

    def __init__(self, cnf):
        StreamCipher.__init__(self, cnf)

    def set_secret_key(self, key, mask=np.ones(secret_key_len)):
        StreamCipher.set_secret_key(self, key, mask)

    def __copy__(self):
        copy_e0 = E0(self.cnf)

        copy_e0.substitution = self.substitution
        copy_e0.key_stream = self.key_stream
        copy_e0.secret_key = self.secret_key
        copy_e0.secret_mask = self.secret_mask

        return copy_e0
