import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


def cdf(array:list) -> tuple:
    # Sort the x and y values based on x
    sorted_data = sorted(array)
    x_sorted = sorted_data

    # Calculate the cumulative sum of y values
    cdf = np.cumsum(sorted_data)

    # Normalize the cumulative sum to get the CDF
    cdf_normalized = 100*cdf / cdf[-1]

    return x_sorted, cdf_normalized


def plot_cdf(cdf_results, all_min, all_max, names, save_fig=True, show_fig=False): # TODO: Needs work
    formatter = FuncFormatter(lambda x, _: f'{x:.6f}')
    linestyles = ['-', '--', '-.', ':']
    plt.figure(figsize=(10, 6))

    for i, (cdf, bin_edges, ind_v) in enumerate(cdf_results):
        linestyle = linestyles[i % len(linestyles)]
        plt.plot(bin_edges[1:], cdf, label=f'data_{i}', markersize=1, linestyle=linestyle)
        plt.scatter(ind_v, np.zeros_like(ind_v), s=25, marker='|', linewidths=0.3)

        plt.xlabel('Intervals')
        plt.ylabel('CDF')
        plt.title(f'{names} - CDF of intervals')
        plt.legend()
        plt.gca().xaxis.set_major_formatter(formatter)

    step = (all_max - all_min) / 6
    xticks = np.arange(all_min, all_max + step, step=step)
    plt.xticks(xticks, rotation=45)
    plt.tight_layout()

    if save_fig:
        plt.savefig(f'{names}.png', format='png', dpi=300)
    if show_fig:
        plt.show()
    plt.close()