from copy import copy

from algorithm import MetaAlgorithm
from util import generator, formatter


class TabuSearch(MetaAlgorithm):
    name = "Tabu Search"

    def __init__(self, ts_parameters):
        MetaAlgorithm.__init__(self, ts_parameters)
        self.iteration_size = None
        self.upgrade_count = ts_parameters["upgrade_count"]

    def get_iteration_size(self):
        return self.iteration_size

    def start(self, mf_parameters):
        algorithm = mf_parameters["crypto_algorithm"][0]
        self.iteration_size = algorithm.secret_key_len
        it = 1
        it_upgrades = 0
        mf_calls = 0
        locals_list = []

        self.print_info(algorithm.name)
        center, value = self.__get_new_center(algorithm, mf_parameters)
        best = (center, value)

        while not self.stop_condition(it, mf_calls, len(locals_list)):
            self.print_iteration_header(it)
            iteration_hash = {}
            updated = False
            for x in self.__get_neighbourhood(center):
                key = formatter.format_array(x)
                if key in iteration_hash or key in self.value_hash:
                    hashed = True
                    value, mf_log = self.value_hash[key], ""
                else:
                    hashed = False
                    mf = self.minimization_function(mf_parameters)
                    value, mf_log = mf.compute(x)
                    mf_calls += 1
                    iteration_hash[key] = value

                if not hashed and self.comparator(best, (x, value)) > 0:
                    best = (x, value)
                    updated = True
                    it_upgrades += 1

                self.print_mf_log(hashed, key, value, mf_log)

                if self.upgrade_count <= it_upgrades:
                    break

            self.value_hash.update(iteration_hash)

            if updated:
                center = best[0]
            else:
                locals_list.append(best)
                self.print_local_info(best)
                center, value = self.__get_new_center(algorithm, mf_parameters)
                best = (center, value)

            it += 1
            it_upgrades = 0

        return locals_list

    def __get_new_center(self, algorithm, mf_parameters):
        center = generator.generate_mask(algorithm.secret_key_len, self.s)
        key = formatter.format_array(center)
        it = 0
        while key in self.value_hash and it < 100:
            center = generator.generate_mask(algorithm.secret_key_len, self.s)
            key = formatter.format_array(center)
            it += 1

        mf = self.minimization_function(mf_parameters)
        value, mf_log = mf.compute(center)
        self.value_hash[formatter.format_array(center)] = value
        return center, value

    @staticmethod
    def __get_neighbourhood(vector):
        for i in range(len(vector)):
            new_vector = copy(vector)
            new_vector[i] = not new_vector[i]
            yield new_vector

    def print_mf_log(self, hashed, key, value, mf_log):
        with open(self.log_file, 'a') as f:
            f.write("------------------------------------------------------\n")
            if hashed:
                f.write("mask: %s in tabu list\n" % key)
                f.write("with value: %.7g\n" % value)
            else:
                f.write("start prediction with mask: %s\n" % key)
                f.write(mf_log)
                f.write("end prediction with value: %.7g\n" % value)
