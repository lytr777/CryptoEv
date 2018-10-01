import matplotlib.pyplot as plt

from plot import Plot


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

        xs, ys, cs = [], [], []
        xss, yss = [], []
        color, i = 0, 0
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
            if color != c and len(xss) > 0:
                xs.append(xss)
                ys.append(yss)
                cs.append(color)

                xss = [xss[-1]]
                yss = [yss[-1]]

            xss.append(i)
            yss.append(best.value)
            color, i = c, i + 1

        if len(xss) > 0:
            xs.append(xss)
            ys.append(yss)
            cs.append(color)

        return xs, ys, cs

    def draw_line(self, ax, line):
        for i in range(len(line.xs)):
            ax.semilogy(line.xs[i], line.ys[i], c=self.cmap(line.cs[i]), lw=self.lw)
