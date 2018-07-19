from plot import Plot


class BasePlot(Plot):
    def __init__(self, parameters):
        Plot.__init__(self, parameters)

    def process_iterations(self, its):
        points = []
        for it in its:
            best = None
            for case in it:
                if best is None or self.comparator(best, case.mv()) > 0:
                    best = case.mv()

            points.append(best.value)

        return points

    def draw_line(self, ax, data):
        ax.semilogy(range(len(data)), data, lw=self.lw)
