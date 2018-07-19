import matplotlib.pyplot as plt


class Plot:
    def __init__(self, parameters):
        self.comparator = parameters["comparator"]

        self.lw = parameters["lw"] if ("lw" in parameters) else 2

        self.lines = []

    def add_line(self, its):
        data = self.process_iterations(its)
        self.lines.append(data)

    def add_lines(self, its_list):
        for its in its_list:
            self.add_line(its)

    def process_iterations(self, its):
        raise NotImplementedError

    def show(self, configuration=111):
        figure = plt.figure()

        mod = (configuration / 100) * (configuration / 10 % 10)
        for i in range(len(self.lines)):
            ax = figure.add_subplot(configuration + (i % mod))
            self.draw_line(ax, self.lines[i])

        plt.show()

    def draw_line(self, ax, data):
        raise NotImplementedError
