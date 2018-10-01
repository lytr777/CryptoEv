class Parser:
    def __init__(self):
        pass

    def parse_for_path(self, path):
        return self.parse(self.__read(path))

    def parse(self, data):
        raise NotImplementedError

    @staticmethod
    def __read(path):
        with open(path) as f:
            lines = f.readlines()
            data = [str(x).split("\n")[0] for x in lines]

            return data
