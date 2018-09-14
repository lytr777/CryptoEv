import matplotlib.pyplot as plt


class Line:
    def __init__(self, xs, ys, cs, label):
        self.xs = xs
        self.ys = ys
        self.cs = cs
        self.label = label


class Plot:
    def __init__(self, parameters):
        self.comparator = parameters["comparator"]

        self.lw = parameters["lw"] if ("lw" in parameters) else 2
        self.x_label = parameters["x_label"] if ("x_label" in parameters) else None
        self.y_label = parameters["y_label"] if ("y_label" in parameters) else None

        self.lines = []

    def add_line(self, its, label=None):
        xs, ys, cs = self.process_iterations(its)
        line = Line(xs, ys, cs, label)
        self.lines.append(line)

    def process_iterations(self, its):
        raise NotImplementedError

    def show(self, configuration=111):
        self.__process_lines(configuration)
        plt.show()

    def save(self, path, configuration=111):
        figure = self.__process_lines(configuration)
        plt.draw()
        figure.savefig(path)

    def __process_lines(self, configuration):
        figure = plt.figure()

        mod = (configuration / 100) * (configuration / 10 % 10)
        for i in range(len(self.lines)):
            ax = figure.add_subplot(configuration + (i % mod))
            self.draw_line(ax, self.lines[i])

            if self.x_label is not None:
                ax.xaxis.set_label_position('bottom')
                ax.set_xlabel(self.x_label)

            if self.y_label is not None:
                ax.yaxis.set_label_position('left')
                ax.set_ylabel(self.y_label)

        return figure

    def draw_line(self, ax, line):
        raise NotImplementedError
