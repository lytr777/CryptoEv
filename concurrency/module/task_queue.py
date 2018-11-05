class TaskQueue:
    def __init__(self, **kwargs):
        self.tasks = []

    def pop(self):
        if self.__len__() == 0:
            raise Exception("Queue is empty")

        return self.tasks.pop(0)

    def fill(self, filler):
        self.tasks = filler.get_tasks()

    def __len__(self):
        return len(self.tasks)

    def __iter__(self):
        while self.__len__() > 0:
            yield self.pop()
