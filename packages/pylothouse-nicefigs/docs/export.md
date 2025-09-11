# Export

`ExportSpec` controls file output for each render.

- `path`: base path or file path; if the suffix doesn’t match a format, a suffix is added per format
- `formats`: any of `png`, `pdf`, `svg` (default `["png"]`)
- `dpi`: raster DPI for `png`
- `tight_layout`: when `true`, exports with `bbox_inches="tight"`
- `metadata`: `dict` of metadata forwarded to `matplotlib.pyplot.savefig`

## Relative paths

- When rendering via CLI without `--out`, relative export paths resolve against the YAML directory. With `--out` or `resolve_export_relative_to="cwd"` in API, relative export paths resolve against the current working directory.
