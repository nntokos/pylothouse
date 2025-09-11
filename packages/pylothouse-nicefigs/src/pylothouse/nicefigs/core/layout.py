from matplotlib import pyplot as plt

def make_grid(layout, sharex=False, sharey=False):
    use_constrained = (layout.wspace is None) or (layout.hspace is None)
    fig, axes = plt.subplots(
        layout.rows,
        layout.cols,
        squeeze=False,
        sharex=layout.shared_x or sharex,
        sharey=layout.shared_y or sharey,
        constrained_layout=use_constrained,
    )
    # If user supplied both spacings explicitly, override constrained layout
    if not use_constrained:
        fig.subplots_adjust(wspace=layout.wspace, hspace=layout.hspace)
    else:
        # Partial override: if one provided, adjust only that after initial auto layout
        if layout.wspace is not None or layout.hspace is not None:
            cur = fig.subplotpars
            fig.subplots_adjust(
                wspace=layout.wspace if layout.wspace is not None else cur.wspace,
                hspace=layout.hspace if layout.hspace is not None else cur.hspace,
            )
    return fig, axes
