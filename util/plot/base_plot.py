from util.plot.plot import Plot


class BasePlot(Plot):
    def __init__(self, parameters):
        Plot.__init__(self, parameters)

    def process_iterations(self, its):
        xs, ys = its
        return xs, ys, None

    def draw_line(self, ax, line):
        if line.label is None:
            ax.plot(line.xs, line.ys, lw=self.lw)
        else:
            ax.plot(line.xs, line.ys, lw=self.lw, label=line.label)
            ax.legend()