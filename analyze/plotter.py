import matplotlib.pyplot as plt


def show_dispersion(ks, k_tuples, configuration=111):
    size = (configuration / 100) * (configuration / 10 % 10)
    if len(ks) > size:
        raise Exception("plot grid is small")

    figure = plt.figure()
    i = 0
    for k in ks:
        points, lines = k_tuples[k]

        for j in range(len(points)):
            points[j] = list(set(points[j]))

        for j in range(len(points)):
            ax = figure.add_subplot(configuration + i)
            ax.semilogy([j] * len(points[j]), points[j], 'oc')

        for j in [0, 1]:
            ax = figure.add_subplot(configuration + i)
            ax.semilogy(range(len(lines[j])), lines[j], 'k', lw=1, ls='dashed')
        for j in [2]:
            ax = figure.add_subplot(configuration + i)
            ax.semilogy(range(len(lines[j])), lines[j], 'r', lw=2, ls='solid')

        i += 1
        print "%d/%d" % (i, len(ks))

    plt.show()


def show_value_dependency(ks, lines, my_line=None):
    figure = plt.figure()
    for label, line in lines:
        ax = figure.add_subplot(111)
        ax.semilogy(ks, line, label=label)
        ax.legend()

    if my_line is not None:
        kss = range(10, 1001)
        ys = [my_line(k) for k in kss]
        ax = figure.add_subplot(111)
        ax.semilogy(kss, ys, label="my")
        ax.legend()

    plt.show()
