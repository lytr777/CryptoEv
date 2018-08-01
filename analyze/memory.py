import hashlib
import pickle


class Memory:
    def __init__(self):
        self.buf_size = 65536
        self.dir = "./analyze/memory/"

    def get_hash(self, path):
        md5 = hashlib.md5()

        with open(path, 'rb') as f:
            data = f.read(self.buf_size)
            while data:
                md5.update(data)
                data = f.read(self.buf_size)

        return md5.hexdigest()

    def save(self, path, chunk):
        file_hash = self.get_hash(path)

        if not chunk.is_empty():
            pickle.dump(chunk.key_tuples, open(self.dir + file_hash, "w+"))

    def load(self, path):
        file_hash = self.get_hash(path)
        try:
            key_tuples = pickle.load(open(self.dir + file_hash, "rb"))
            return Chunk(path, key_tuples)
        except IOError:
            return Chunk(path, {})


class Chunk:
    def __init__(self, path, key_tuples, overwrite=False):
        self.path = path
        self.key_tuples = key_tuples
        self.overwrite = overwrite

    def overwriting(self, flag):
        self.overwrite = flag

    def set(self, key, key_tuple):
        if key in self.key_tuples and not self.overwrite:
            raise Exception("tuple for key = %s already exist" % key)
        else:
            self.key_tuples[key] = key_tuple

    def get(self, key, default=None):
        if key in self.key_tuples:
            return self.key_tuples[key]
        else:
            return default

    def is_empty(self):
        return len(self.key_tuples.keys()) == 0

    def __contains__(self, key):
        return not self.overwrite and key in self.key_tuples
