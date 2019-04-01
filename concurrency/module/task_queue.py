class TaskQueue:
    def __init__(self, **kwargs):
        self._tasks = []

    def pop(self):
        if self.__len__() == 0:
            raise Exception("Queue is empty")

        return self._tasks.pop(0)

    def fill(self, tasks):
        for task in tasks:
            self._tasks.append(task)

    def __len__(self):
        return len(self._tasks)

    def clear(self):
        self._tasks = []

    def __iter__(self):
        while self.__len__() > 0:
            yield self.pop()
