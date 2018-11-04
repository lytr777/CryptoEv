class QueueOfGeneratedTasks:
    def __init__(self, **kwargs):
        self.count = 0
        self.generator = None

    def pop(self):
        if self.count == 0:
            raise Exception("Queue is empty")

        task = self.generator.generate()
        self.count -= 1

        return task

    def fill(self, filler):
        self.generator = filler.get_generator()
        self.count = filler.get_count()

    def __len__(self):
        return self.count

    def __iter__(self):
        while self.count > 0:
            yield self.pop()
