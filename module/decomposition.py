import numpy as np
from copy import copy

from util import formatter, generator


def decomposition(value_hash):
    def __decomposition(mask, case, d, m_function, mf_parameters):
        new_mask = copy(mask)
        zero_index = []
        for i in range(len(new_mask)):
            if new_mask[i] == 0:
                zero_index.append(i)

        if len(zero_index) < d:
            d = len(zero_index)
        choice = np.random.choice(len(zero_index), d, replace=False)

        decomposition_indices = []
        for e in choice:
            decomposition_indices.append(zero_index[e])
            new_mask[zero_index[e]] = not new_mask[zero_index[e]]

        key = formatter.format_array(new_mask)
        if key in value_hash:
            return value_hash[key]

        cases = []
        secret_keys = generator.generate_decomposition_key_set(case.secret_key, decomposition_indices)
        for i in range(len(secret_keys)):
            case_i = copy(case)

            case_i.set_secret_key(secret_keys[i], new_mask)
            cases.append(case_i)

        print "== decomposition from " + formatter.format_array(mask) + " to " + formatter.format_array(new_mask)
        mf_parameters_copy = copy(mf_parameters)
        mf_parameters_copy["N"] = len(cases)
        mf = m_function(mf_parameters_copy, case.key_stream)
        value, stats = mf.compute(new_mask, cases)
        return value

    return __decomposition
