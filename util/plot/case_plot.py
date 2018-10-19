from plot import Plot


class CasePlot(Plot):
    def __init__(self, parameters):
        Plot.__init__(self, parameters)

    def process_iterations(self, its):
        xs, ys = [], []
        i = 0
        for it in its:
            best = it[0]
            for case in it:
                if self.comparator.compare(best.mv(), case.mv()) > 0:
                    best = case

            ys.append(best.value)
            xs.append(i)
            i += 1

        return xs, ys, None

    def draw_line(self, ax, line):
        if line.label is None:
            ax.semilogy(line.xs, line.ys, lw=self.lw)
        else:
            ax.semilogy(line.xs, line.ys, lw=self.lw, label=line.label)
            ax.legend()
