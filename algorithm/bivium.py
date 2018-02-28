import numpy as np
from copy import copy

from model.cnf_model import Clause, Var
from util.parser import parse_solution


class Bivium:
    __key_stream_start = 443
    key_stream_len = 200

    __secret_key_start = 1
    secret_key_len = 177

    def __init__(self, cnf):
        self.cnf_link = cnf
        self.cnf = None

        self.key_stream = None
        self.secret_key = None
        self.secret_mask = None

        self.time = None
        self.status = None
        self.solution = []

    def set_key_stream(self, key):
        if self.key_stream_len != len(key):
            raise Exception("Key stream must contain " + str(self.key_stream_len) + " bits")

        self.key_stream = key

    def set_secret_key(self, key, mask=np.ones(secret_key_len)):
        if self.secret_key_len != len(key):
            raise Exception("Secret key must contain " + str(self.secret_key_len) + " bits")

        if self.secret_key_len != len(key):
            raise Exception("Secret mask must contain " + str(self.secret_key_len) + " bits")

        self.secret_key = key
        self.secret_mask = mask

    def __substitute_key_stream(self):
        for i in range(len(self.key_stream)):
            cl = Clause()
            cl.add_var(Var(self.__key_stream_start + i, not self.key_stream[i]))
            self.cnf.add_clause(cl)

    def __substitute_secret_key(self):
        for i in range(len(self.secret_key)):
            if self.secret_mask[i]:
                cl = Clause()
                cl.add_var(Var(self.__secret_key_start + i, not self.secret_key[i]))
                self.cnf.add_clause(cl)

    def write_to(self, file_path):
        self.cnf = copy(self.cnf_link)
        if self.key_stream is not None:
            self.__substitute_key_stream()
        if self.secret_key is not None:
            self.__substitute_secret_key()

        with open(file_path, 'w') as f:
            f.write(str(self.cnf))

        self.cnf = None

    def mark_solved(self, time, status, out_path):
        self.time = time
        self.status = status

        self.solution = parse_solution(out_path)

    def get_solution_secret_key(self):
        start = self.__secret_key_start - 1
        end = start + self.secret_key_len
        return self.__get_key(start, end)

    def get_solution_key_stream(self):
        start = self.__key_stream_start - 1
        end = start + self.key_stream_len
        return self.__get_key(start, end)

    def __get_key(self, start, end):
        if len(self.solution) == 0:
            raise Exception("Solution is not specified")

        return self.solution[start:end]

    def __copy__(self):
        copy_bivium = Bivium(self.cnf_link)

        copy_bivium.key_stream = self.key_stream
        copy_bivium.secret_key = self.secret_key
        copy_bivium.secret_mask = self.secret_mask

        return copy_bivium