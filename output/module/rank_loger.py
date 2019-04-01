import threading

from algorithm.module.rank_test import RankCases


class RankLogger:
    def __init__(self, log_file):
        s_file = log_file.split('/')
        if 'rank' not in s_file[-1]:
            s_file[-1] = 'rank_%s' % s_file[-1]
        self.log_file = '/'.join(s_file)

        open(self.log_file, 'w+').close()
        self.lock = threading.Lock()

    def write_it(self, i):
        self.lock.acquire()
        with open(self.log_file, "a") as f:
            f.write('iteration step: %d\n' % i)
            f.write('------------------------------------------------------\n')
        self.lock.release()

    def write(self, x, y, res):
        if isinstance(x[2], RankCases) and isinstance(y[2], RankCases):
            self.lock.acquire()
            with open(self.log_file, "a") as f:
                f.write('%s: %s\n' % (str(x[0]), str(x[2])))
                f.write('%s: %s\n' % (str(y[0]), str(y[2])))
                f.write('Result: %s\n' % str(res))
                f.write('------------------------------------------------------\n')
            self.lock.release()

    def deferred_write(self, x, y, res):
        self.write(x, y, res)
