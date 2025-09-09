from .api import render, render_spec, load_config, rc_context, new_figure, draw_panels, save
from .core import layers as _layers      # registers line/scatter/hist
from . import plugins as _plugins        # registers cdf/ecdf

__all__ = [
    "render",
    "render_spec",
    "load_config",
    "rc_context",
    "new_figure",
    "draw_panels",
    "save",
]
