# pylothouse-nicefigs

Config-first, journal-ready matplotlib figures for papers. Define figures in YAML, render via CLI or API.

## Quick start

```bash
pip install -e .[dev]
nicefigs render examples/fig_cdf_hist.yml
```

See `examples/` for sample configs.

## Use from Python

- Render from a YAML file on disk (data paths in YAML resolve relative to the YAML’s folder):
```python
import nicefigs as nf

# Load YAML and render; export.path resolves relative to the YAML by default
spec = nf.load_config("examples/fig_cdf_hist.yml")
# Optionally override output and resolve relative to CWD instead of YAML dir
spec.export.path = "./out/fig_cdf_hist.pdf"
nf.render_spec(spec, resolve_export_relative_to="cwd")
```

- Render by injecting a pure-Python DataFrame (no CSV needed):
  - In your YAML (or dict), set series.data to a key name (e.g., "snr").
  - Pass a dict of DataFrames where keys match series.data.
```python
import pandas as pd
import nicefigs as nf

# Minimal config as a Python dict (could also be a YAML file with the same fields)
cfg = {
    "size": {"width": 89, "height": 67, "unit": "mm"},
    "layout": {"rows": 1, "cols": 1},
    "panels": [
        {"series": [
            {"type": "cdf", "data": "snr", "x": "snr", "label": "A"}
        ]}
    ],
    "export": {"path": "./figure.pdf", "formats": ["pdf"]},
}

spec = nf.load_config(cfg)
# Prepare DataFrame in Python; the key "snr" matches series.data
snr_df = pd.DataFrame({"snr": [1.2, 0.7, 0.9, 1.5, 1.1]})

# Inject data; with resolve_export_relative_to="cwd", relative export path saves in the current folder
nf.render_spec(spec, external_data={"snr": snr_df}, resolve_export_relative_to="cwd")
```

Notes
- external_data can be a single DataFrame (applied to all series) or a dict[str, DataFrame] keyed by series.data.
- Relative data paths like ./data.csv in YAML are resolved next to the YAML file; absolute paths are unchanged.
- You need matplotlib and pandas installed to render figures.
