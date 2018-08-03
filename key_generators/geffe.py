import numpy as np

from stream_cipher import StreamCipher


class Geffe(StreamCipher):
    key_stream_start = 301
    key_stream_len = 100

    secret_key_start = 1
    secret_key_len = 64

    name = "Geffe"
    tag = "geffe"

    def __init__(self, cnf):
        StreamCipher.__init__(self, cnf)

    def set_secret_key(self, key, mask=np.ones(secret_key_len)):
        StreamCipher.set_secret_key(self, key, mask)
        self.__substitute_secret_key()

    def __copy__(self):
        copy_geffe = Geffe(self.cnf)

        copy_geffe.substitution = self.substitution
        copy_geffe.key_stream = self.key_stream
        copy_geffe.secret_key = self.secret_key
        copy_geffe.secret_mask = self.secret_mask

        return copy_geffe
