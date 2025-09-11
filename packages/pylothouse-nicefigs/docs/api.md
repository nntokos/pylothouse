# Python API

## Import

- `from pylothouse import nicefigs as nf`

## Functions

- `load_config(path_or_dict) -> FigureSpec`
  - Accepts a path (`str`/`Path`) to YAML or a raw `dict` matching the schema
  - Applies `preset`/`theme` if present; expands overlay file references to inline entries; sets `spec.base_dir`
- `render(config_path: str) -> bool`
  - Convenience: load YAML then `render_spec`; returns `True` on success
- `render_spec(spec: FigureSpec, resolve_export_relative_to: "spec"|"cwd" = "spec", external_data=None) -> bool`
  - Renders an in-memory `FigureSpec`; relative export paths resolve against YAML dir (`spec`) or current working directory (`cwd`)
  - `external_data`: `pandas.DataFrame` or `dict[str, DataFrame]`
- `rc_context(spec: FigureSpec)` -> context manager
  - Applies `matplotlib.rcParams` for `size`, `DPI`, `font`, LaTeX preamble; restores on exit
- `new_figure(spec: FigureSpec) -> (Figure, axes)`
  - Creates a subplot grid per `layout`; returns `Figure` and 2D array of `Axes`
- `draw_panels(axes, spec: FigureSpec, external_data=None)`
  - Draws `series` and `overlays` for each panel, applies axes styling and legends; removes unused axes
- `save(fig, export_spec, base_dir: Optional[str])`
  - Saves to each requested format, appending suffixes as needed; resolves relative path against `base_dir`

## Registration

- Importing `pylothouse.nicefigs` registers built-in layers (`line`, `scatter`, `hist`) and plugins (`cdf`, `ecdf`).
