import numpy as np

from block_cipher import BlockCipher


class Present_6_1KP(BlockCipher):
    key_stream_start = 1185
    key_stream_len = 64

    secret_key_start = 1
    secret_key_len = 80

    public_key_start = 81
    public_key_len = 64

    name = "Present_6_1KP"
    tag = "present_6_1kp"

    def __init__(self, cnf):
        BlockCipher.__init__(self, cnf)

    def set_secret_key(self, key, mask=np.ones(secret_key_len)):
        BlockCipher.set_secret_key(self, key, mask)

    def __copy__(self):
        copy_present = Present_6_1KP(self.cnf)

        copy_present.substitution = self.substitution
        copy_present.key_stream = self.key_stream
        copy_present.secret_key = self.secret_key
        copy_present.public_key = self.public_key
        copy_present.secret_mask = self.secret_mask

        return copy_present