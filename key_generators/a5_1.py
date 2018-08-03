import numpy as np

from stream_cipher import StreamCipher


class A5_1(StreamCipher):
    key_stream_start = 8298
    key_stream_len = 128

    secret_key_start = 1
    secret_key_len = 64

    name = "A5/1"
    tag = "a5_1"

    def __init__(self, cnf):
        StreamCipher.__init__(self, cnf)

    def set_secret_key(self, key, mask=np.ones(secret_key_len)):
        StreamCipher.set_secret_key(self, key, mask)

    def __copy__(self):
        copy_a5_1 = A5_1(self.cnf)

        copy_a5_1.substitution = self.substitution
        copy_a5_1.key_stream = self.key_stream
        copy_a5_1.secret_key = self.secret_key
        copy_a5_1.secret_mask = self.secret_mask

        return copy_a5_1
