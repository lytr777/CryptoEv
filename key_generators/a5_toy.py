import numpy as np

from stream_cipher import StreamCipher


class A5_toy(StreamCipher):
    key_stream_start = 3931
    key_stream_len = 80

    secret_key_start = 1
    secret_key_len = 48

    name = "A5/1 48"
    tag = "a5_1 48"

    def __init__(self, cnf):
        StreamCipher.__init__(self, cnf)

    def set_secret_key(self, key, mask=np.ones(secret_key_len)):
        StreamCipher.set_secret_key(self, key, mask)

    def __copy__(self):
        copy_a5_toy = A5_toy(self.cnf)

        copy_a5_toy.substitution = self.substitution
        copy_a5_toy.key_stream = self.key_stream
        copy_a5_toy.secret_key = self.secret_key
        copy_a5_toy.secret_mask = self.secret_mask

        return copy_a5_toy
