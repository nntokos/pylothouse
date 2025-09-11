# Overlays

Overlays are declarative annotations drawn on top of each panel. They’re specified via `OverlaySpec` and rendered by `core/overlays.py`. You can inline overlays in `YAML` or reference a file that contains a list of overlay dicts.

## Supported types

- `vline`: vertical line at `x`
- `hline`: horizontal line at `y`
- `line`: segment from (`x0`, `y0`) to (`x1`, `y1`)
- `point`: marker at (`x`, `y`); size uses `width` if provided (default `30.0`)
- `rect`: rectangle from (`x`, `y`, `width`, `height`) or corners (`x0`, `y0`, `x1`, `y1`)
- `circle`: circle centered at (`x`, `y`) with `radius`
- `annotation`: 
    - Free text placed at (`x`, `y`)
    - Supports `text_dx`/`text_dy` for offsetting text position
    - `text_rotation` specifies rotation in degrees
    - Alignment controls:
      - `text_ha`: horizontal alignment (`"left"` | `"center"` | `"right"`), default `"center"`
      - `text_va`: vertical alignment (`"top"` | `"center"` | `"bottom"` | `"baseline"`), default `"center"`
    - Anchor semantics: the point (`x`, `y`) refers to the specified text anchor given by `text_ha`/`text_va`
- `band`: 
    - Vertical band between `x0` and `x1`
    - Vertical extent defined by `[ymin_frac, ymax_frac]` in Axes fraction coordinates
    - Highlights regions of interest or ranges on the x-axis
    - Underlying implementation uses `axvspan`

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

- For `rect`/`circle` with text, the label is drawn centered with optional offsets; you can also set `text_ha`/`text_va` to change the anchoring
- `band` uses `axvspan` under the hood; `ymin_frac`/`ymax_frac` are clamped to `[0, 1]`
- JSON tip: in `.json` files, use `true`/`false` (booleans) for `show_in_legend`, not strings like `"False"`.
