# Configuration schema

This page documents the full YAML schema validated by Pydantic models in nicefigs. Field names map 1:1 to the classes in `pylothouse.nicefigs.config.models`.

## Top-level `FigureSpec`

- `size`: `Size`
- `font`: `FontSpec`
- `layout`: `LayoutSpec`
- `panels`: `list[PanelSpec]`
- `theme`: `str | null`
- `preset`: `str | null`
- `palette`: `str | null` (default: `okabe_ito`)
- `export`: `ExportSpec`
- `axes_defaults`: `AxesSpec | null`

## `Size`

- `width`: `float` (in `unit`)
- `height`: `float` (in `unit`)
- `unit`: one of `in`, `mm`, `pt` (default: `in`)

## `FontSpec`

- `family`: `str` (default `serif`)
- `size`: `int` (default `9`)
- `weight`: `str` (`normal`|`bold`|`light`, default `normal`)
- `style`: `str` (`normal`|`italic`|`oblique`, default `normal`)
- `use_tex`: `bool` (default `true`)
- `latex_preamble`: `str | null` (default `"\usepackage{amsmath}"`)

## `LayoutSpec`

- `rows`: `int` (default `1`)
- `cols`: `int` (default `1`)
- `wspace`: `float | null` (`None` => auto; default `null`)
- `hspace`: `float | null` (`None` => auto; default `null`)
- `shared_x`: `bool` (default `false`)
- `shared_y`: `bool` (default `false`)

## `ExportSpec`

- `path`: `str` (default `figure.png`)
- `dpi`: `int` (default `300`)
- `formats`: `list["pdf"|"png"|"svg"]` (default `["png"]`)
- `tight_layout`: `bool` (default `true`)
- `metadata`: `dict[str,str]` (default `{}`)

## `PanelSpec`

- `axes`: `AxesSpec`
- `series`: `list[SeriesSpec]`
- `overlays`: `list[OverlaySpec] | list[str] | null`
  - In `YAML` you can list file paths (`.yaml`/`.yml`/`.json`) to be expanded before validation.

## `AxesSpec`

- `title`: `TextLike` (`str | TextSpec | null`)
- `xlabel`: `TextLike`
- `ylabel`: `TextLike`
- `xscale`: `linear`|`log`|`symlog` (default `linear`)
- `yscale`: `linear`|`log`|`symlog` (default `linear`)
- `grid`: `GridSpec`
- `limits`: `{ x: [min, max] | null, y: [min, max] | null }`
- `legend`: `LegendSpec`
- `spines`: `SpinesSpec`
- `xticks`: `AxisTicksSpec`
- `yticks`: `AxisTicksSpec`
- `show_axes_frame`: `bool` (default `true`)
- `show_xlabel`: `bool` (default `true`)
- `show_ylabel`: `bool` (default `true`)
- `show_title`: `bool` (default `true`)

## `TextStyleSpec` (base)

- `family`: `str | null`
- `size`: `float | null`
- `weight`: `str | null`
- `style`: `str | null`
- `color`: `str` (default `black`)

## `TextSpec` (extends `TextStyleSpec`)

- `show`: `bool` (default `true`)
- `text`: `str | null`
- `rotation`: `float | null` (degrees)
- `ha`: `str | null` (horizontal align)
- `va`: `str | null` (vertical align)
- `pad`: `float | null` (points)
- `dx`: `float | null` (offset x)
- `dy`: `float | null` (offset y)
- `dx_unit`: `axes`|`points` (default `axes`)
- `dy_unit`: `axes`|`points` (default `axes`)

## `LegendSpec`

- `show`: `bool` (default `true`)
- `loc`: `str` (matplotlib legend location, default `best`)
- `ncol`: `int` (default `1`)
- `frameon`: `bool` (default `false`)
- `title`: `TextLike`
- `labels`: `list[TextLike] | null`
- `style`: `TextStyleSpec | null` (applied to all legend labels by default)
- `anchor`: `[x, y] | [x, y, w, h] | null` (axes fraction)
- `offset_x`: `float | null` (shift from anchor)
- `offset_y`: `float | null`
- `offset_unit`: `axes`|`points` (default `axes`)

## `GridSpec`

- `show`: `bool` (default `true`)
- `which`: `major`|`minor`|`both` (default `both`)
- `linestyle`: `str` (default `:`)
- `linewidth`: `float` (default `0.5`)
- `color`: `str` (default `#cccccc`)

## `SpinesSpec`

- `show_left`: `bool` (default `true`)
- `show_right`: `bool` (default `true`)
- `show_top`: `bool` (default `true`)
- `show_bottom`: `bool` (default `true`)
- `color`: `str` (default `black`)
- `linewidth`: `float | null`

## `AxisTicksSpec` (extends `TextStyleSpec`)

- `show`: `bool` (default `true`)
- `rotation`: `float | null`
- `direction`: `in`|`out`|`inout` | `null`
- `length`: `float | null`
- `width`: `float | null`
- `locations`: `list[float] | null`
- `range`: `[min, max, step] | null`
- `fmt`: `TickFormatterSpec | str | callable | null`
- `labels`: `list[TextLike] | null` (per-tick overrides)

## `TickFormatterSpec`

- `kind`: `printf`|`strfmt`|`sci`|`eng`|`percent`|`thousands`|`si`|`date`|`custom` (default `strfmt`)
- `pattern`: `str | null`
- `sci_limits`: `list[int] | null`
- `unit`: `str | null`
- `places`: `int | null`
- `scale`: `float | null`
- `prefix`: `str | null`
- `suffix`: `str | null`
- `use_mathtext`: `bool | null`
- `expression`: `str | null`
- `wrap_mathtext`: `bool` (default `false`)
- `bold`: `bool` (default `false`)
- `italic`: `bool` (default `false`)

## `SeriesSpec`

- `type`: `line`|`scatter`|`bar`|`hist`|`cdf`|`ecdf`|`heatmap`
- `x`: `str | null` (column)
- `y`: `str | null` (column)
- `data`: `str | dict | path | callable | DataFrame | null`
- `query`: `str | null` (pandas query string)
- `style`: `LineSpec`
- `label`: `TextLike`
- `bins`: `int | null` (hist only)

Note: Built-in layers are `line`, `scatter`, `hist`, `cdf`, `ecdf`. Other types like `bar`/`heatmap` require a plugin or custom layer registration.

## `LineSpec`

- `color`: `str` (default `C0`)
- `width`: `float` (default `1.0`)
- `style`: `solid`|`dashed`|`dotted`|`dashdot` (default `solid`)
- `marker`: `str | null`

## `OverlaySpec`

- `type`: `line`|`hline`|`vline`|`point`|`rect`|`circle`|`annotation`|`band`
- `color`: `str | null`
- `edgecolor`: `str | null`
- `facecolor`: `str | null`
- `fill`: `bool | null`
- `alpha`: `float | null`
- `linewidth`: `float | null`
- `linestyle`: `str | null`
- `label`: `str | null`
- `show_in_legend`: `bool` (default `false`)
- `zorder`: `int | null`
- `x`,`y`,`x0`,`x1`,`y0`,`y1`: `float | null`
- `radius`,`width`,`height`: `float | null`
- `text`: `str | null`
- `text_dx`,`text_dy`: `float` (default `0`)
- `text_align`: `str | null`
- `ymin_frac`,`ymax_frac`: `float | null`

## Semantics and units

- Figure size `unit` controls `TextSpec` `dx`/`dy` when `dx_unit`/`dy_unit == "points"`. Values in `mm`/`pt` are converted to inches internally.
- When `dx_unit`/`dy_unit == "axes"`, offsets are expressed in data units and scaled by the current axis range and axes pixel size.
- Legend `offset_unit` `axes` means offsets are fractions of the axes box; `points` means absolute typographic points.

## Merging axes defaults

- If `figure.axes_defaults` is set, each `panel.axes` is deep-merged over it; unspecified fields inherit defaults.

## Overlays from files

- In `YAML`, `panel.overlays` may include file paths (`.yml`/`.yaml`/`.json`). The loader expands those into inline overlay dicts relative to the YAML directory before validation.
