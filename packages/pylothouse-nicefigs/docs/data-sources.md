# Data sources

nicefigs loads pandas DataFrames from flexible inputs via `io.readers.load_dataframe`.

## Supported inputs

- `pandas.DataFrame`: returned as-is
- `callable`: called with no args; result is re-processed recursively
- `dict` spec:
  - keys: `dataframe`|`df` (direct `DataFrame`), or `loader`|`call`|`func` (`callable`), or `path`/`file`/`csv`/`parquet`/`json`
  - `reader`: `csv`|`parquet`|`json` (optional; inferred from file extension)
  - `kwargs`: `dict` of keyword args forwarded to pandas readers
- `str`/`Path`: path to `csv`/`parquet`/`json` (extension inferred; default `csv`)

## Path resolution

- Relative paths are resolved against `FigureSpec.base_dir` (the folder that contains the YAML); `resolve_export_relative_to="cwd"` only affects export path, not data loading.

## External data injection

- `render_spec(spec, external_data=...)`
  - If `external_data` is a `dict[str, DataFrame]`, `series.data` should be a matching string key.
  - If `external_data` is a single `DataFrame`, that DF is used for all series.
  - If no `external_data` match, `series.data` is loaded using the above rules.

## Filtering

- `SeriesSpec.query`: optional pandas query expression applied after loading.
