# Examples

## Sample figure

- `examples/fig_cdf_hist.yml` renders multiple panels with `cdf`, `hist`, `line`, custom ticks, and overlays.

## Render locally

- From the package folder:

```bash
nicefigs render examples/fig_cdf_hist.yml
```

## Overlay file

- `examples/overlay_data.json` contains entries like:

```json
[
  {"type": "vline", "x": 15.89, "linestyle": "dash", "color": "blue"},
  {"type": "rect", "x0": 3.43, "x1": 66.928, "y0": 0.0, "y1": 1.0, "facecolor": "red", "alpha": 0.2}
]
```

## Usage tips

- Keep data files next to the YAML for portable relative paths
- Use `preset` to standardize sizes across a project
- Prefer `legend.labels` to ensure stable ordering and text
