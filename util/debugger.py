import sys
import threading

from datetime import datetime


class Debugger:
    def __init__(self, debug_file=None, verb=0):
        self.debug_file = debug_file
        self.verb = verb
        self.s_queue = []
        self.lock = threading.Lock()

    def deferred_write(self, verb, level=0, *strs):
        if self.verb < verb:
            return

        self.lock.acquire()
        s = self.__prepare_str(level, *strs)
        self.s_queue.append(s)
        self.lock.release()

    def write(self, verb, level=0, *strs):
        if self.verb < verb:
            return

        self.lock.acquire()
        f = sys.stdout if self.debug_file is None else open(self.debug_file, "a")

        while len(self.s_queue) > 0:
            s = self.s_queue.pop(0)
            f.write(s)

        if self.verb >= verb:
            s = self.__prepare_str(level, *strs)
            f.write(s)

        if self.debug_file is not None:
            f.close()

        self.lock.release()

    def __prepare_str(self, level, *strs):
        s = " ".join(strs)
        ss = ["(%s) %s%s\n" % (datetime.today(), self.lp(level), line) for line in s.split('\n')]
        s = "".join(ss)
        return s

    @staticmethod
    def lp(level):
        return "--" * level + " "
