from __future__ import annotations
from pathlib import Path
from typing import Optional, Union, List
from ruamel.yaml import YAML
import json
from .models import FigureSpec  # OverlaySpec intentionally not imported for pre-validation expansion
from .presets.journals import apply_journal_preset
from .presets.themes import apply_theme

def _read_yaml(path: Union[str, Path]) -> dict:
    yaml = YAML(typ="safe")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.load(f) or {}

def _read_overlay_file(path: Path) -> List[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Overlay file not found: {path}")
    if path.suffix.lower() in (".yml", ".yaml"):
        data = _read_yaml(path)
    elif path.suffix.lower() == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        raise ValueError(f"Unsupported overlay file extension: {path.suffix}")
    if not isinstance(data, list):
        raise TypeError(f"Overlay file must contain a top-level list: {path}")
    out: List[dict] = []
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            raise TypeError(f"Overlay entry #{i} in {path} must be an object/dict")
        out.append(entry)
    return out

def _expand_overlay_files_in_raw_cfg(cfg: dict, base_dir: Optional[str]):
    if 'panels' not in cfg or not isinstance(cfg['panels'], list):
        return
    for panel in cfg['panels']:
        ovs = panel.get('overlays')
        if not ovs or not isinstance(ovs, list):
            continue
        expanded: List[dict] = []
        for item in ovs:
            if isinstance(item, str):
                p = Path(item)
                if not p.is_absolute() and base_dir:
                    p = Path(base_dir) / p
                file_specs = _read_overlay_file(p.resolve())  # returns List[dict]
                expanded.extend(file_specs)
            elif isinstance(item, dict):
                expanded.append(item)
            else:
                # OverlaySpec instances should not appear before validation; treat as error
                raise TypeError("panel.overlays entries must be file path str or dict before validation")
        panel['overlays'] = expanded

def load_config(path_or_dict) -> FigureSpec:
    base_dir: Optional[str] = None
    if isinstance(path_or_dict, (str, Path)):
        cfg_path = Path(path_or_dict)
        base_dir = str(cfg_path.resolve().parent)
        cfg = _read_yaml(cfg_path)
    elif isinstance(path_or_dict, dict):
        cfg = path_or_dict
    else:
        raise TypeError("load_config expects a path or a dict")

    preset = cfg.get("preset")
    theme = cfg.get("theme")
    if preset:
        cfg = apply_journal_preset(cfg, preset)
    if theme:
        cfg = apply_theme(cfg, theme)

    # Expand overlays BEFORE validation (raw dicts only) so FigureSpec/PanelSpec validators perform actual OverlaySpec validation
    _expand_overlay_files_in_raw_cfg(cfg, base_dir)

    spec = FigureSpec.model_validate(cfg)
    spec.base_dir = base_dir
    return spec
