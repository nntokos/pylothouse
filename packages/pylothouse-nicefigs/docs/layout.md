# Layout

`LayoutSpec` controls the subplot grid and spacing. The grid is created with `matplotlib.pyplot.subplots`.

## Fields

- `rows`, `cols`: grid size
- `shared_x`, `shared_y`: share axes across panels
- `wspace`, `hspace`: subplot spacing
  - If either is `null`, `constrained_layout` is enabled; you can partially override one spacing after auto layout

## Behavior

- The figure may create more axes than panels; any extra axes are removed or hidden so empty panels aren’t shown.
