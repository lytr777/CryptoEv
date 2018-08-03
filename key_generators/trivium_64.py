import numpy as np

from stream_cipher import StreamCipher


class Trivium_64(StreamCipher):
    key_stream_start = 398
    key_stream_len = 75

    secret_key_start = 1
    secret_key_len = 64

    name = "Trivium 64"
    tag = "trivium_64"

    def __init__(self, cnf):
        StreamCipher.__init__(self, cnf)

    def set_secret_key(self, key, mask=np.ones(secret_key_len)):
        StreamCipher.set_secret_key(self, key, mask)

    def __copy__(self):
        copy_tr_64 = Trivium_64(self.cnf)

        copy_tr_64.substitution = self.substitution
        copy_tr_64.key_stream = self.key_stream
        copy_tr_64.secret_key = self.secret_key
        copy_tr_64.secret_mask = self.secret_mask

        return copy_tr_64
