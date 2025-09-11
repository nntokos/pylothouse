# Validation

- The `YAML`/`dict` config is validated using Pydantic models (`config/models.py`).
- Before validation, the loader expands `panel.overlays` file paths into inline overlay dicts.
- Validators coerce strings to `TextSpec` where applicable and validate list shapes.

## Linting

- `validation/lint.py` provides a simple `lint(spec)` that warns when `font.size < 6`.

## Common validation behaviors

- `TextLike` fields (`title`/`xlabel`/`ylabel`/`legend.title`/`labels`/`series.label`) accept `str` or `dict` and are coerced to `TextSpec`
- `AxisTicksSpec.labels` entries accept `str`|`dict`|`TextSpec`|`null`; errors for invalid types
- Overlay file paths must be expanded by the loader; `PanelSpec` validator raises if raw strings remain
