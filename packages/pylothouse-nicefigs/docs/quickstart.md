# Getting started

Install and render the example figure.

- Install
    - `pip install -e .[dev]` inside `packages/pylothouse-nicefigs`
- Render the example
    - `nicefigs render examples/fig_cdf_hist.yml`

What happens

- The YAML is parsed and validated (Pydantic models)
- `preset`/`theme` are applied if present
- Overlays loaded from external JSON/YAML are expanded
- Matplotlib `rcParams` are set from `size`/`font`/`export`
- A grid of subplots is created per `layout`
- Each panel draws its `series` and `overlays`, then axes styling is applied
- The figure is exported to the configured `formats`

Minimal YAML

- Define `size`, `layout`, `panels`, and `export`. Data paths are resolved relative to the YAML file by default.

```yaml
size: {width: 89, height: 67, unit: mm}
layout: {rows: 1, cols: 1}
panels:
  - series:
      - { type: line, data: "./data_line.csv", x: x, y: y, label: "Line" }
export: { path: "./figure", formats: [png, pdf], dpi: 300 }
```

From Python

- You can use the API to load and render; see Python API page for details.
