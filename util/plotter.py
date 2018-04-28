import matplotlib.pyplot as plt


def show_plot(data, configuration=111):
    # plt.ion()
    data_metrics = []
    for d in data:
        metrics = []
        for i in range(len(d)):
            metrics.append(d[i][1])
        data_metrics.append(metrics)

    figure =  plt.figure()
    # for i in range(len(data)):
    #     fig = plt.figure()
    #     figures.append(fig)

    axes = []
    for i in range(len(data)):
        ax = figure.add_subplot(configuration + i)
        axes.append(ax)

    for i in range(len(data_metrics)):
        axes[i].semilogy(range(len(data_metrics[i])), data_metrics[i], lw=2)
        # axes[i].set_ybound(2**38, 2**63)

    plt.show()
