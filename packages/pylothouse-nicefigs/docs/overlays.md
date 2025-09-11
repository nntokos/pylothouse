# Overlays

Overlays are declarative annotations drawn on top of each panel. They’re specified via `OverlaySpec` and rendered by `core/overlays.py`. You can inline overlays in `YAML` or reference a file that contains a list of overlay dicts.

## Supported types

- `vline`: vertical line at `x`
- `hline`: horizontal line at `y`
- `line`: segment from (`x0`, `y0`) to (`x1`, `y1`)
- `point`: marker at (`x`, `y`); size uses `width` if provided (default `30.0`)
- `rect`: rectangle from (`x`, `y`, `width`, `height`) or corners (`x0`, `y0`, `x1`, `y1`)
- `circle`: circle centered at (`x`, `y`) with `radius`
- `annotation`: free text at (`x`, `y`) with `text_dx`/`text_dy` and `text_align`
- `band`: vertical band between `x0` and `x1` with vertical extent `[ymin_frac, ymax_frac]` in `Axes` fraction coords

## Style fields

- `color`, `facecolor`, `edgecolor`, `alpha`, `linewidth`, `linestyle`, `zorder`
- `facecolor`/`edgecolor` override `color` when present; `linestyle` is normalized via `resolve_linestyle`

## Legend

- `show_in_legend`: when `true`, the created artist is given `label` (or empty string) so it appears in the legend

## Error handling

- Drawing is fail-soft: malformed specs are skipped and don’t break the render

## Example (external file)

- `examples/overlay_data.json` contains a list of overlay entries used by `examples/fig_cdf_hist.yml`.

## Notes

- For `rect`/`circle` with text, the label is drawn centered with optional offsets
- `band` uses `axvspan` under the hood; `ymin_frac`/`ymax_frac` are clamped to `[0, 1]`
- JSON tip: in `.json` files, use `true`/`false` (booleans) for `show_in_legend`, not strings like `"False"`.
