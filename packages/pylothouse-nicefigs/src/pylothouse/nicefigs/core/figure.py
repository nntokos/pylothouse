from typing import List
from matplotlib import pyplot as plt
from .layout import make_grid
from .axes import setup_axes, maybe_legend
from ..io.readers import load_dataframe
from .registry import make as make_layer

def new_figure(spec):
    fig, axes = make_grid(spec.layout)
    return fig, axes

def _resolve_df(series_spec, spec, external_data):
    # 1) If external_data provided, try it first
    if external_data is not None:
        # dict: use series.data as key if it's a string
        if isinstance(external_data, dict) and isinstance(series_spec.data, str) and series_spec.data in external_data:
            return load_dataframe(external_data[series_spec.data], base_dir=spec.base_dir)
        # single object: treat as the whole dataset
        if not isinstance(external_data, dict):
            return load_dataframe(external_data, base_dir=spec.base_dir)

    # 2) Fall back to spec-provided data (path/DF/dict/callable)
    if series_spec.data is not None:
        return load_dataframe(series_spec.data, base_dir=spec.base_dir)

    # 3) Nothing
    return None

def draw_panels(axes, spec, external_data=None):
    # Iterate panels; axes is 2D array
    idx = 0
    for r in range(spec.layout.rows):
        for c in range(spec.layout.cols):
            if idx >= len(spec.panels):
                continue
            panel = spec.panels[idx]
            ax = axes[r][c]
            setup_axes(ax, panel.axes)
            # Draw series
            for s in panel.series:
                df = _resolve_df(s, spec, external_data)
                if df is not None and s.query:
                    df = df.query(s.query)
                layer = make_layer(s.type, spec=s)
                layer.draw(ax, df)
            maybe_legend(ax, panel.axes.legend)
            idx += 1
    return axes
