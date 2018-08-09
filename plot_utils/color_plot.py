import matplotlib.pyplot as plt

from plot import Plot
from util import formatter


class ColorPlot(Plot):
    def __init__(self, parameters):
        Plot.__init__(self, parameters)
        self.min_N = parameters["min_N"]
        self.max_N = parameters["max_N"]
        self.cmap = parameters["cmap"] if ("cmap" in parameters) else plt.cm.viridis

    def process_iterations(self, its):
        assert self.max_N > self.min_N
        divider = (self.max_N - self.min_N) / 256.
        times_hash = {}

        data = []
        points = []
        color = None
        for it in its:
            best = None
            for case in it:
                if best is None or self.comparator(best.mv(), case.mv()) > 0:
                    best = case

            key = str(best.mask)
            if len(best.times) > 0:
                times_hash[key] = times = best.times
            else:
                times = times_hash[key]

            c = int((len(times) - self.min_N) / divider)
            if color is not None and color != c:
                data.append((points, self.cmap(color)))
                last_point = points[len(points) - 1]
                points = [last_point]

            points.append(best.value)
            color = c

        if len(points) > 0:
            data.append((points, self.cmap(color)))

        return data

    def draw_line(self, ax, data):
        i = 0
        for ys, color in data:
            ax.semilogy(range(i, i + len(ys)), ys, c=color, lw=self.lw)
            i += len(ys) - 1
