class TaskFiller:
    def __init__(self, **kwargs):
        self.count = kwargs["count"]
        self.generator = kwargs["generator"]
        self.complexity = kwargs["complexity"]

    def get_count(self):
        return self.count

    def get_generator(self):
        return self.generator

    def get_complexity(self):
        return self.complexity
