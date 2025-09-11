# CLI

## Command

- `nicefigs render CONFIG [--out PATH] [--override key=value]...`

## Options

- `--out`: override `export.path`; when provided, relative paths resolve against `CWD`
- `--override`: apply dot-path overrides (e.g., `size.width=89`, `axes_defaults.legend.show=false`)
  - Values are type-cast: integers or floats when numeric, booleans for `true`/`false` (case-insensitive), otherwise strings

## Examples

- `nicefigs render examples/fig_cdf_hist.yml`
- `nicefigs render examples/fig_cdf_hist.yml --out ./out/fig.pdf`
- `nicefigs render examples/fig_cdf_hist.yml --override font.size=10 --override layout.shared_y=true`

## Exit status

- Exits nonzero on unhandled exceptions (e.g., YAML parse error, missing files)
