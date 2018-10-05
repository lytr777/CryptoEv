import numpy as np


class Mutation:
    name = "mutation"

    def __init__(self, **kwargs):
        pass

    def mutate(self, backdoor):
        raise NotImplementedError

    def __str__(self):
        return self.name


class UniformMutation(Mutation):
    def __init__(self, **kwargs):
        Mutation.__init__(self, **kwargs)
        self.scale = float(kwargs["scale"])

    def mutate(self, backdoor):
        new_v = backdoor.get_mask()
        p = self.scale / len(new_v)
        flag = True
        while flag:
            distribution = np.random.rand(len(new_v))

            for d in distribution:
                if p >= d:
                    flag = False

        for i in range(len(new_v)):
            if p >= distribution[i]:
                new_v[i] = not new_v[i]

        return backdoor.get_copy(new_v)

    def __str__(self):
        return "mutation: uniform (%f)" % self.scale


# def neighbour_mutation(backdoor):
#     new_v = backdoor.get_mask()
#     pos = np.random.randint(len(new_v))
#     new_v[pos] = not new_v[pos]
#     return backdoor.get_copy(new_v)
#
#
# def swap_mutation(backdoor):
#     new_v = backdoor.get_mask()
#
#     zero_indices = []
#     nonzero_indices = []
#     for i in range(len(new_v)):
#         if new_v[i] == 0:
#             zero_indices.append(i)
#         else:
#             nonzero_indices.append(i)
#
#     zero_pos = np.random.randint(len(zero_indices))
#     nonzero_pos = np.random.randint(len(nonzero_indices))
#
#     new_v[zero_indices[zero_pos]] = not new_v[zero_indices[zero_pos]]
#     new_v[nonzero_indices[nonzero_pos]] = not new_v[nonzero_indices[nonzero_pos]]
#
#     return backdoor.get_copy(new_v)
