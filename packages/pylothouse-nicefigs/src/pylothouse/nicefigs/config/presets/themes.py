from copy import deepcopy

_THEMES = {
    "light": {"palette": "okabe_ito"},
    "dark": {"palette": "okabe_ito"},  # placeholder for dark rcParams
}

def apply_theme(cfg: dict, name: str) -> dict:
    base = deepcopy(_THEMES.get(name, {}))
    base.update(cfg)  # user config wins
    return base
