import numpy as np
from copy import copy

from util import formatter


class Decomposition:
    name = "decomposition"

    def __init__(self, value_hash, d, break_time):
        self.value_hash = value_hash
        self.d = d
        self.break_time = break_time

    def decompose(self, mask, case, m_function, mf_parameters):
        new_mask = copy(mask)
        zero_index = []
        for i in range(len(new_mask)):
            if new_mask[i] == 0:
                zero_index.append(i)

        if len(zero_index) < self.d:
            self.d = len(zero_index)
        choice = np.random.choice(len(zero_index), self.d, replace=False)

        decomposition_indices = []
        for e in choice:
            decomposition_indices.append(zero_index[e])
            new_mask[zero_index[e]] = not new_mask[zero_index[e]]

        key = formatter.format_array(new_mask)
        if key in self.value_hash:
            return self.value_hash[key]

        cases = []
        secret_keys = self.generate_decomposition_key_set(case.secret_key, decomposition_indices)
        for i in range(len(secret_keys)):
            case_i = copy(case)

            case_i.set_secret_key(secret_keys[i], new_mask)
            cases.append(case_i)

        d_log = "== decomposition from %s to %s\n" % (formatter.format_array(mask), formatter.format_array(new_mask))
        mf_parameters_copy = copy(mf_parameters)
        mf_parameters_copy["N"] = len(cases)
        mf = m_function(mf_parameters_copy, case.key_stream)
        value, mf_log = mf.compute(new_mask, cases)
        return value, d_log + mf_log

    def generate_decomposition_key_set(self, base_key, indices):
        keys = [base_key]
        indices_copy = copy(indices)
        while len(indices_copy) > 0:
            index = indices_copy.pop()
            new_keys = []
            for key in keys:
                for i in range(2):
                    copy_key = copy(key)
                    copy_key[index] = i
                    new_keys.append(copy_key)
            keys = new_keys

        return keys

    def __str__(self):
        return self.name
