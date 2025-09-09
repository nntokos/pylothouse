from __future__ import annotations
from pathlib import Path
from ruamel.yaml import YAML
from .models import FigureSpec
from .presets.journals import apply_journal_preset
from .presets.themes import apply_theme

def _read_yaml(path: str | Path) -> dict:
    yaml = YAML(typ="safe")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.load(f) or {}

def load_config(path_or_dict) -> FigureSpec:
    base_dir: str | None = None
    if isinstance(path_or_dict, (str, Path)):
        cfg_path = Path(path_or_dict)
        base_dir = str(cfg_path.resolve().parent)
        cfg = _read_yaml(cfg_path)
    elif isinstance(path_or_dict, dict):
        cfg = path_or_dict
    else:
        raise TypeError("load_config expects a path or a dict")

    # Apply preset/theme early to fill defaults
    preset = cfg.get("preset")
    theme = cfg.get("theme")
    if preset:
        cfg = apply_journal_preset(cfg, preset)
    if theme:
        cfg = apply_theme(cfg, theme)

    spec = FigureSpec.model_validate(cfg)
    spec.base_dir = base_dir
    return spec
