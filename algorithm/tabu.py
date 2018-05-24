from copy import copy

from algorithm import MetaAlgorithm
from util import generator, formatter


class TabuSearch(MetaAlgorithm):
    name = "Tabu Search"

    def __init__(self, ts_parameters):
        MetaAlgorithm.__init__(self, ts_parameters)
        self.iteration_size = None
        self.update_count = ts_parameters["update_count"]

    def get_iteration_size(self):
        return self.iteration_size

    def start(self, mf_parameters):
        algorithm = mf_parameters["crypto_algorithm"][0]
        self.iteration_size = algorithm.secret_key_len
        it = 1
        it_updates = 0
        mf_calls = 0
        locals_list = []
        tabu_list = {}

        self.print_info(algorithm.name)
        center, value = self.__get_new_center(algorithm, mf_parameters)
        best = (center, value)

        while not self.stop_condition(it, mf_calls, len(locals_list)):
            self.print_iteration_header(it)
            updated = False
            for x in self.__get_neighbourhood(center):
                key = formatter.format_array(x)
                if key in self.value_hash:
                    hashed = True
                    value, mf_log = self.value_hash[key], ""
                else:
                    hashed = False
                    mf = self.minimization_function(mf_parameters)
                    result = mf.compute(x)
                    value, mf_log = result[0], result[1]
                    mf_calls += 1
                    self.value_hash[key] = value

                if key in tabu_list:
                    self.print_tabu_log(key, value)
                else:
                    if self.comparator(best, (x, value)) > 0:
                        best = (x, value)
                        updated = True
                        it_updates += 1

                    self.print_mf_log(hashed, key, value, mf_log)

                if self.update_count <= it_updates:
                    break

            if updated:
                center_key = formatter.format_array(best[0])
                tabu_list[center_key] = best[1]
                center = best[0]
            else:
                locals_list.append(best)
                self.print_local_info(best)
                center, value = self.__get_new_center(algorithm, mf_parameters)
                best = (center, value)

            it += 1
            it_updates = 0

        return locals_list

    def __get_new_center(self, algorithm, mf_parameters):
        center = generator.generate_mask(algorithm.secret_key_len, self.s)
        key = formatter.format_array(center)

        if key in self.value_hash:
            value = self.value_hash[key]
        else:
            mf = self.minimization_function(mf_parameters)
            result = mf.compute(center)
            value = result[0]
            self.value_hash[key] = value

        return center, value

    @staticmethod
    def __get_neighbourhood(vector):
        for i in range(len(vector)):
            new_vector = copy(vector)
            new_vector[i] = not new_vector[i]
            yield new_vector

    def print_tabu_log(self, key, value):
        with open(self.log_file, 'a') as f:
            f.write("------------------------------------------------------\n")
            f.write("mask: %s in tabu list\n" % key)
            f.write("with value: %.7g\n" % value)
