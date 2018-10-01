import threading

from datetime import datetime


class Debugger:
    def __init__(self, debug_file, verb=0):
        self.debug_file = debug_file
        open(debug_file, 'w+').close()
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
        with open(self.debug_file, "a") as f:
            while len(self.s_queue) > 0:
                s = self.s_queue.pop(0)
                f.write(s)

            f.write(self.__prepare_str(level, *strs))
        self.lock.release()

    def __prepare_str(self, level, *strs):
        s = " ".join(strs)
        ss = ["(%s) %s%s\n" % (datetime.today(), self.__lp(level), line) for line in s.split('\n')]
        s = "".join(ss)
        return s

    def __lp(self, level):
        return "--" * level + " "


class DebuggerStub:
    def __init__(self):
        pass

    def deferred_write(self, verb, level=0, *strs):
        pass

    def write(self, verb, level=0, *strs):
        pass
