import matplotlib.pyplot as plt


def show_plot(data):
    # plt.ion()
    data_metrics = []
    for d in data:
        metrics = []
        for i in range(len(d)):
            metrics.append(d[i][1])
        data_metrics.append(metrics)

    figures = []
    for i in range(len(data)):
        fig = plt.figure()
        figures.append(fig)

    axes = []
    for i in range(len(data)):
        ax = figures[i].add_subplot(111)
        axes.append(ax)

    for i in range(len(data_metrics)):
        axes[i].semilogy(range(len(data_metrics[i])), data_metrics[i], lw=2)

    plt.show()
