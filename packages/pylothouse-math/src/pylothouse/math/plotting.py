import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.transforms as mtransforms

def plot(x, y, title, xlabel='x', ylabel='y', show=True, save=False, filename='plot.png', fig=None, color='b', linestyle='-'):
    """

    Args:
        x: [list] x-axis values
        y: [list] y-axis values
        title: [str] title of the plot
        xlabel: [str] label for x-axis
        ylabel: [str] label for y-axis
        show: [bool] whether to show the plot. Default is True
        save: [bool] whether to save the plot. Default is False
        filename: [str] name of the file to save the plot. If save is False, this argument is ignored. Default is 'plot.png'
        fig: [matplotlib.figure.Figure] figure object to plot on. If None, a new figure is created

    Returns: [matplotlib.figure.Figure, matplotlib.axes.Axes] figure and axes objects

    """
    if not save and not show:
        print('pylothouse-math.plotting.plot_on_fig called with neither show nor save. Nothing to do.')
        return
    if save and not filename.endswith('.png'):
        raise ValueError('Filename must end with .png')

    if fig is None:
        fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x, y, color=color, linestyle=linestyle)
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    if save:
        plt.savefig(filename)
    if show:
        plt.show()
    return fig, ax


def plot_multiple(x, ys, labels, title, xlabel='x', ylabel='y', show=True, save=False, filename='plot.png', fig=None, color='b', linestyle='-'):
    """

    Args:
        x: [list] x-axis values
        ys: [list of lists] y-axis values
        labels: [list of str] labels for each line
        title: [str] title of the plot
        xlabel: [str] label for x-axis
        ylabel: [str] label for y-axis
        show: [bool] whether to show the plot. Default is True
        save: [bool] whether to save the plot. Default is False
        filename: [str] name of the file to save the plot. If save is False, this argument is ignored. Default is 'plot.png'
        fig: [matplotlib.figure.Figure] figure object to plot on. If None, a new figure is created

    Returns: [matplotlib.figure.Figure, matplotlib.axes.Axes] figure and axes objects

    """
    if not save and not show:
        print('pylothouse-math.plotting.plot_on_fig called with neither show nor save. Nothing to do.')
        return
    if save and not filename.endswith('.png'):
        raise ValueError('Filename must end with .png')

    if fig is None:
        fig = plt.figure()
    ax = fig.add_subplot(111)
    for y, label in zip(ys, labels):
        ax.plot(x, y, label=label, color=color, linestyle=linestyle)
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    ax.legend()
    if save:
        plt.savefig(filename)
    if show:
        plt.show()
    return fig, ax

def text_height(ax, fontsize):
    """
    Calculate height of text in pixels
    Args:
        fontsize: [int] font size in points

    Returns: [float] height of text in axis coordinates

    """

    text_height_ax_coord = ax.transData.inverted().transform((fontsize, fontsize))[1]
    fig_origin_height_ax_coord = ax.transData.inverted().transform((0, 0))[1]

    real_text_height_ax_coord = abs(text_height_ax_coord - fig_origin_height_ax_coord)

    return real_text_height_ax_coord

def text_width(ax, text, fontsize):
    """
    Calculate width of text in pixels
    Args:
        text: [str] text to calculate width of
        fontsize: [int] font size in points

    Returns: [float] width of text in axis coordinates

    """
    temp_fig, temp_ax = plt.subplots()

    text_bbox = temp_ax.text(0,0,text, fontsize=fontsize).get_window_extent()
    text_width_ax_coord = ax.transData.inverted().transform((text_bbox.width, 0))[0]
    fig_origin_width_ax_coord = ax.transData.inverted().transform((0, 0))[0]
    real_text_width_ax_coord = abs(text_width_ax_coord - fig_origin_width_ax_coord)
    plt.close(temp_fig)
    return real_text_width_ax_coord
