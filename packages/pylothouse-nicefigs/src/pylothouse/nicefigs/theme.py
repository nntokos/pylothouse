from __future__ import annotations

import matplotlib as mpl

mpl_default_style = {
    "figure.figsize": (8, 5),
    "figure.dpi": 120,
    "axes.grid": True,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "grid.linestyle": ":",
    "grid.alpha": 0.5,
    "font.size": 11,
}


def set_mpl_theme(style: dict | None = None) -> None:
    """Apply a pleasant default Matplotlib theme.

    Args:
        style: Optional dict of rcParams to overlay on defaults.
    """
    rc = dict(mpl_default_style)
    if style:
        rc.update(style)
    mpl.rcParams.update(rc)
# pylothouse-nicefigs

