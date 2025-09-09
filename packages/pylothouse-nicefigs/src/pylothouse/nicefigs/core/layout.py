from matplotlib import pyplot as plt

def make_grid(layout, sharex=False, sharey=False):
    fig, axes = plt.subplots(layout.rows, layout.cols, squeeze=False,
                             sharex=layout.shared_x or sharex,
                             sharey=layout.shared_y or sharey)
    fig.subplots_adjust(wspace=layout.wspace, hspace=layout.hspace)
    return fig, axes
