# Layers

Layers are rendering primitives registered in the layer registry. The built-ins are loaded when you import `nicefigs` (see `core/layers.py` and `plugins/cdf.py`).

## Built-in types

- `line`: `ax.plot(x, y)`
  - Uses `LineSpec`: `linewidth`, `linestyle`, `color`, `marker`, `label`
- `scatter`: `ax.scatter(x, y)`
  - Uses `marker`, `color`, `label`; `linewidth`/`linestyle` aren’t used by `matplotlib` scatter
- `hist`: `ax.hist(x)`
  - Uses `bins` (default `30`) and `label`
- `cdf`: empirical CDF (sorted `x` vs `i/n`) with `y` in `[0,1]`
  - Style: `linewidth`, `linestyle`, `marker`, `color`, `label`; `y`-limits forced to `[0,1]`
- `ecdf`: alias of `cdf`

## Extending

- Register a new layer using `core.registry.register("name")`. Implement `draw(self, ax, df)` on a subclass of `Layer`.

## Linestyle aliases

- `solid`|`-` ; `dashed`|`--`|`dash` ; `dotted`|`:`|`dot` ; `dashdot`|`-.`|`dash-dot`
