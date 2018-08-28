from copy import copy
import numpy as np

from graph_utils import clause_graph as cg


class LevelMutation:
    def __init__(self, cnf, algorithm):
        self.graph = cg.build(cnf)
        self.__build_levels(algorithm)

        self.skl = algorithm.secret_key_len

    def __get_level(self, last_level):
        prev_level = self.levels[-1]
        new_level = cg.get_next_level(self.graph, prev_level)
        for old_level in self.levels:
            new_level -= old_level

        return new_level, new_level.intersection(last_level)

    def __build_levels(self, algorithm):
        start_level = set(range(algorithm.secret_key_start, algorithm.secret_key_len + algorithm.secret_key_start))
        last_level = set(range(algorithm.key_stream_start, algorithm.key_stream_len + algorithm.key_stream_start))
        c_last_level = copy(last_level)

        self.levels = [start_level]
        while len(c_last_level) > 0:
            level, inter = self.__get_level(last_level)
            self.levels.append(level)
            c_last_level -= inter

        self.levels.append(last_level)

    def mutate(self, backdoor):
        new_mask = copy(backdoor.mask)
        core_p = 1. / self.skl
        opt_p = 1. / (self.skl + np.count_nonzero(new_mask))

        distribution = np.random.rand(len(new_mask))
        p1 = core_p / 2 + opt_p
        p2 = p1 + opt_p

        add_list = []
        for i in range(len(new_mask)):
            if p1 >= distribution[i]:
                new_mask[i] = not new_mask[i]
            elif p2 >= distribution[i]:
                new_mask[i] = not new_mask[i]
                if new_mask[i] == 0:
                    add_list.append(i)

        new_backdoor = backdoor.get_copy(new_mask)

        for i in add_list:
            var = new_backdoor.vars[i]

            i = 0
            while i < len(self.levels) and var not in self.levels[i]:
                i += 1

            assert i < len(self.levels)
            if i + 1 < len(self.levels):
                next_level = self.levels[i + 1]
                node = self.graph.nodes[var - 1]

                possible = next_level.intersection(set([n.i for n in node.edges]))

                priority_vars = []
                for v in possible:
                    n = self.graph.nodes[v - 1]
                    priority_vars.append((len(n.edges), n.i))
                priority_vars = sorted(priority_vars)[::-1]

                for _, v in priority_vars:
                    if new_backdoor.find(v) < 0:
                        new_backdoor.add(v)
                        print "new variable: %d" % v
                        break
            else:
                new_backdoor.add(var)

        return new_backdoor
