def setup_axes(ax, axes_spec):
    if axes_spec.title: ax.set_title(axes_spec.title)
    if axes_spec.xlabel: ax.set_xlabel(axes_spec.xlabel)
    if axes_spec.ylabel: ax.set_ylabel(axes_spec.ylabel)
    ax.set_xscale(axes_spec.xscale)
    ax.set_yscale(axes_spec.yscale)
    if axes_spec.grid:
        ax.grid(True, which="both", linestyle=":", linewidth=0.5)
    lims = axes_spec.limits
    if lims.get("x"): ax.set_xlim(*lims["x"])
    if lims.get("y"): ax.set_ylim(*lims["y"])
    return ax

def maybe_legend(ax, legend):
    if legend.show:
        ax.legend(loc=legend.loc, ncol=legend.ncol, frameon=legend.frameon)
