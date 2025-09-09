from copy import deepcopy

_PRESETS = {
    "ieee_single_col": {"size": {"width": 89, "height": 67, "unit": "mm"}, "font": {"size": 8}},
    "ieee_double_col": {"size": {"width": 183, "height": 67, "unit": "mm"}, "font": {"size": 8}},
    "nature_single_col": {"size": {"width": 89, "height": 89, "unit": "mm"}, "font": {"size": 9}},
}

def apply_journal_preset(cfg: dict, name: str) -> dict:
    base = deepcopy(_PRESETS.get(name, {}))
    # shallow-merge base into cfg where not provided
    def merge(a, b):
        for k, v in b.items():
            if isinstance(v, dict) and isinstance(a.get(k), dict):
                merge(a[k], v)
            else:
                a.setdefault(k, v)
    merge(cfg, base)
    return cfg
