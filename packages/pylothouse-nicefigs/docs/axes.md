# Axes and styling

AxesSpec controls scales, limits, grid, spines, ticks, titles, and labels. All text accepts `TextSpec` for content and styling.

## Scales and limits

- `xscale` / `yscale`: `linear`|`log`|`symlog`
- `limits`: `{ x: [min, max] | null, y: [min, max] | null }`

## Grid and spines

- `grid.show` + `which`/`linestyle`/`linewidth`/`color`
- `spines`: visibility per side, `color`, `linewidth`
- `show_axes_frame`: hide all spines when `false`

## Titles and labels (`TextSpec`)

- `text`, `show`, `rotation`, `pad`, `ha`/`va`, `family`, `size`, `weight`, `style`, `color`
- Offsets: `dx`/`dy` with units
  - `axes`: values in data units converted relative to current axis range
  - `points`: absolute offsets in figure size units (`in`/`mm`/`pt`)

## Legend

- `legend.show` toggles visibility
- Handles/labels gathered from artists with labels that don’t start with `"_"`
- `legend.labels`: explicit list of `TextLike` overrides; if more labels than handles, dummy lines are added
- `legend.title`: `TextLike` (default `"Legend"` if omitted and `legend.show` true)
- `anchor`: `bbox_to_anchor` `[x,y]` or `[x,y,w,h]` in axes coords
- `offset_x`/`offset_y`: extra shift in `axes` or `points` per `offset_unit`

## Tick labels and marks

- `AxisTicksSpec` merges text style into tick labels; `tick_params` applies size/color/rotation
- Placement: set explicit `locations` or generate from `range` `[min, max, step]`
- Formatting:
  - `fmt` can be callable, empty string (hide), printf `"%.2f"`, or format string `"{:.2f}"`
  - If `font.use_tex` is `true`, labels are wrapped to preserve bold/italic per style
- Per-label overrides: `AxisTicksSpec.labels` accepts a list of `TextLike` applied after global style

## LaTeX integration heuristics

- If `font.use_tex` is `true` and label/title text is plain, bold/italic styles are wrapped with `\textbf`/`\textit`
- Existing LaTeX (backslashes), explicit `$...$`, or pre-wrapped text are left as-is
