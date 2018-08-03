import numpy as np

from stream_cipher import StreamCipher


class Bivium(StreamCipher):
    key_stream_start = 443
    key_stream_len = 200

    secret_key_start = 1
    secret_key_len = 177

    name = "Bivium"
    tag = "bivium"

    def __init__(self, cnf):
        StreamCipher.__init__(self, cnf)

    def set_secret_key(self, key, mask=np.ones(secret_key_len)):
        StreamCipher.set_secret_key(self, key, mask)

    def __copy__(self):
        copy_bivium = Bivium(self.cnf)

        copy_bivium.substitution = self.substitution
        copy_bivium.key_stream = self.key_stream
        copy_bivium.secret_key = self.secret_key
        copy_bivium.secret_mask = self.secret_mask

        return copy_bivium
