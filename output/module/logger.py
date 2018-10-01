import threading


class Logger:
    def __init__(self, log_file):
        self.log_file = log_file
        open(log_file, 'w+').close()
        self.s_queue = []
        self.lock = threading.Lock()

    def deferred_write(self, *strs):
        self.lock.acquire()
        for s in strs:
            self.s_queue.append(self.__prepare_str(s))
        self.lock.release()

    def write(self, *strs):
        self.lock.acquire()
        with open(self.log_file, "a") as f:
            while len(self.s_queue) > 0:
                s = self.s_queue.pop(0)
                f.write(s)

            for s in strs:
                f.write(self.__prepare_str(s))
        self.lock.release()

    def __prepare_str(self, s):
        return "%s\n" % s if s[-1] != '\n' else s


class LoggerStub:
    def __init__(self):
        pass

    def deferred_write(self, *strs):
        pass

    def write(self, *strs):
        pass
