import numpy as np
from copy import copy


class BackdoorList:
    def __init__(self, variables=()):
        self.var_list = list(variables)
        self.value_list = np.ones(len(variables), dtype=np.int)

    def __getitem__(self, i):
        return self.value_list[i]

    def __setitem__(self, i, value):
        self.value_list[i] = value

    def __str__(self):
        return str(self.value_list)

    def __len__(self):
        return len(self.value_list)

    def __copy__(self):
        backdoor_list = BackdoorList(self.var_list)
        backdoor_list.value_list = copy(self.value_list)

        return backdoor_list

    def get_var(self, i):
        return self.var_list[i]

    def get_key(self):
        s = "["
        for i in range(self.__len__()):
            if self.value_list[i]:
                s += "%s " % self.var_list[i]
        s = s[:-1] + "](%d)" % np.count_nonzero(self.value_list)
        return s
