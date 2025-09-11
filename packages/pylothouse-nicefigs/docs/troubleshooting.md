# Troubleshooting

## LaTeX errors

- Symptom: `RuntimeError: Failed to process string with tex because latex could not be found`
- Fix: Install a LaTeX distribution or set `font.use_tex: false`

## File not found

- Data path or overlay file isn’t found
- Paths in `YAML` are resolved relative to the YAML file’s directory; check typos and working directory

## Blank/empty panels

- When `panels < rows*cols`, extra axes are removed; ensure your panel count matches the intended layout

## Legend not showing

- Artists must have non-empty labels; for overlays, set `show_in_legend: true` and `label`

## Tick labels formatting

- `fmt` supports callables, printf (`"%.2f"`), or format strings (`"{:.2f}"`)
- If ticks don’t change, confirm `xticks`/`yticks.locations` or `range` were set

## Offsets not moving text

- `dx`/`dy` with `axes` units depend on current axis ranges; consider `points` units for absolute shifts

## CDF looks wrong

- Ensure `x` column exists and contains numeric data; `ECDF` uses sorted `x` and `i/n`
