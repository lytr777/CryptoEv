from key_generator import StreamCipher


class BubbleVsInsert(StreamCipher):
    secret_key_start = 1
    secret_key_len = 128

    name = "BubbleVsInsert_8_8"
    tag = "bubble_vs_insert"

    def __init__(self, cnf):
        StreamCipher.__init__(self, cnf)

    def __copy__(self):
        copy_bvsi = BubbleVsInsert(self.cnf)
        copy_bvsi.substitutions = self.substitutions

        return copy_bvsi
