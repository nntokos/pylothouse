# Extending nicefigs

You can add new plot types (layers) and plugins without modifying core code.

## Custom layer

- Implement a subclass of `Layer` with a `draw(self, ax, df)` method
- Register it with `core.registry.register("name")`

### Example

```python
# my_layers.py
from pylothouse.nicefigs.core.layers import Layer
from pylothouse.nicefigs.core.registry import register

@register("bar")
class BarLayer(Layer):
    def draw(self, ax, df):
        # expects categorical x and numeric y
        ax.bar(df[self.spec.x], df[self.spec.y],
               color=self.spec.style.color,
               label=self.spec.label_text)
```

### Usage in YAML

```yaml
panels:
  - series:
      - { type: bar, data: "./bars.csv", x: category, y: value, label: "Bars" }
```

## Plugin modules

- Place your module on the `PYTHONPATH` and import it before rendering so its `@register` calls run
- Alternatively, add an import in `pylothouse.nicefigs.plugins.__init__` if it’s part of your codebase

## Linestyle helpers

- Use `core.utils.resolve_linestyle` to normalize user styles (`solid`, `dashed`, `dotted`, `dashdot` or symbols `-`, `--`, `:`, `-.`)

## Legend behavior

- Use `label=self.spec.label_text` on artists; omit or set to `"_nolegend_"` to hide
- For overlays, set `show_in_legend: true` and `label` in the overlay spec

## Testing tips

- Create a small `DataFrame` inline and `render_spec` with `resolve_export_relative_to="cwd"` to generate a temporary output
- Prefer deterministic inputs to make visual diffs stable
