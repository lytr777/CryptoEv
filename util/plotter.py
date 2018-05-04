import matplotlib.pyplot as plt


def show_plot(data, configuration=111):
    # plt.ion()
    max_size = 0
    data_metrics = []
    for d in data:
        metrics = []
        max_size = max(max_size, len(d))
        for i in range(len(d)):
            metrics.append(d[i][1])
        data_metrics.append(metrics)

    metrics = []
    for i in range(max_size):
        metrics.append(4.64428e+08)
    data_metrics.append(metrics)

    figure = plt.figure()

    mod = (configuration / 100) * (configuration / 10 % 10)
    axes = []
    for i in range(len(data_metrics)):
        ax = figure.add_subplot(configuration + (i % mod))
        axes.append(ax)

    for i in range(len(data_metrics)):
        axes[i].semilogy(range(len(data_metrics[i])), data_metrics[i], lw=2)
        axes[i].set_ybound(2**26, 2**62)

    plt.show()
