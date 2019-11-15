from key_generator import StreamCipher


class BubbleVsSelection(StreamCipher):
    secret_key_start = 1
    secret_key_len = 64

    name = "BubbleVsSelection_8_8"
    tag = "bubble_vs_selection"

    def __init__(self, cnf):
        StreamCipher.__init__(self, cnf)

    def __copy__(self):
        copy_bvss = BubbleVsSelection(self.cnf)
        copy_bvss.substitutions = self.substitutions

        return copy_bvss
