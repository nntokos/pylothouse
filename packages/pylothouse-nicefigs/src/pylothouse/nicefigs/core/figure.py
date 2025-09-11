from typing import List, Optional
from matplotlib import pyplot as plt
from .layout import make_grid
from .axes import setup_axes, maybe_legend
from ..io.readers import load_dataframe
from .registry import make as make_layer
from copy import deepcopy
from ..config.models import AxesSpec
from .overlays import draw_overlay

def new_figure(spec):
    fig, axes = make_grid(spec.layout)
    return fig, axes

def _deep_merge(a: dict, b: dict) -> dict:
    out = deepcopy(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out

def _merge_axes_specs(fig_defaults: Optional[AxesSpec], panel_axes: AxesSpec) -> AxesSpec:
    if fig_defaults is None:
        return panel_axes
    base = fig_defaults.model_dump(exclude_unset=True)
    override = panel_axes.model_dump(exclude_unset=True)
    merged = _deep_merge(base, override)
    # Re-validate so validators convert nested dicts → TextSpec, etc.
    return AxesSpec.model_validate(merged)

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

    return None

def draw_panels(axes, spec, external_data=None):
    # Iterate panels; axes is 2D array
    idx = 0
    total_slots = spec.layout.rows * spec.layout.cols
    for r in range(spec.layout.rows):
        for c in range(spec.layout.cols):
            slot_index = r * spec.layout.cols + c
            if slot_index >= len(spec.panels):
                # defer removal until after loop to avoid altering indices mid-iteration
                continue
            panel = spec.panels[idx]
            merged_axes = _merge_axes_specs(spec.axes_defaults, panel.axes)
            ax = axes[r][c]
            # Draw series
            for s in panel.series:
                df = _resolve_df(s, spec, external_data)
                if df is not None and s.query:
                    df = df.query(s.query)
                layer = make_layer(s.type, spec=s)
                layer.draw(ax, df)
            if panel.overlays is not None:
                for o in panel.overlays:
                    if getattr(o, 'type', None) is None:
                        continue
                    draw_overlay(ax, o, global_font=spec.font)
            setup_axes(ax, merged_axes, spec.font, size_unit=spec.size.unit)
            maybe_legend(ax, panel.axes.legend, spec.font)
            idx += 1
    # Remove or hide unused axes (slots beyond defined panels)
    if len(spec.panels) < total_slots:
        flat = [axes[r][c] for r in range(spec.layout.rows) for c in range(spec.layout.cols)]
        for i, ax in enumerate(flat):
            if i >= len(spec.panels):
                try:
                    ax.remove()
                except Exception:
                    try:
                        ax.set_visible(False)
                    except Exception:
                        pass
    return axes
