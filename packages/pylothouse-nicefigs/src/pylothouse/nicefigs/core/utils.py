def mm_to_in(mm: float) -> float:
    return mm / 25.4

def in_to_mm(inch: float) -> float:
    return inch * 25.4

def pt_to_in(pt: float) -> float:
    return pt / 72.0

def in_to_pt(inch: float) -> float:
    return inch * 72.0

# Unified linestyle resolution
_LINESTYLE_ALIASES = {
    "solid": "-",
    "-": "-",
    "--": "--",
    "dashed": "--",
    "dash": "--",
    ":": ":",
    "dotted": ":",
    "dot": ":",
    "-.": "-.",
    "dashdot": "-.",
    "dash-dot": "-.",
}

def resolve_linestyle(style):
    if not style:
        return "-"
    s = str(style).strip().lower()
    return _LINESTYLE_ALIASES.get(s, style)
