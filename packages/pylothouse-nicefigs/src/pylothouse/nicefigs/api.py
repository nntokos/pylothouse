from .config.loader import load_config as _load_config
from .core.style import rc_context
from .core.figure import new_figure, draw_panels
from .core.export import save
# Ensure built-in layers/plugins are registered when using the API directly
from .core import layers as _layers  # noqa: F401
from . import plugins as _plugins    # noqa: F401

def load_config(path_or_dict):
    return _load_config(path_or_dict)

def render(config_path: str):
    spec = _load_config(config_path)
    return render_spec(spec)

def render_spec(spec, resolve_export_relative_to: str = "spec", external_data=None):
    """
    Render a loaded FigureSpec.
    resolve_export_relative_to:
      - "spec" (default): resolve relative export paths against the YAML config dir
      - "cwd": resolve relative export paths against the current working directory
    external_data:
      - Optional pandas.DataFrame applied to all series, or dict[str, DataFrame]
        where series.data references the dict key instead of a file path.
    """
    from matplotlib import pyplot as plt
    base_dir = spec.base_dir if resolve_export_relative_to != "cwd" else None
    with rc_context(spec):
        fig, axes = new_figure(spec)
        draw_panels(axes, spec, external_data=external_data)
        save(fig, spec.export, base_dir=base_dir)
    return True
