class TaskFiller:
    def __init__(self, **kwargs):
        self.tasks = kwargs["tasks"]
        self.complexity = kwargs["complexity"]

    def get_tasks(self):
        return self.tasks

    def get_complexity(self):
        return self.complexity
