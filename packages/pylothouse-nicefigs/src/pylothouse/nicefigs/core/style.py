from contextlib import contextmanager
from matplotlib import rcParams
from .utils import mm_to_in

def _apply_font(font):
    # Base typography
    rcParams["font.family"] = font.family
    rcParams["font.size"]   = font.size
    rcParams["font.weight"] = font.weight
    rcParams["font.style"]  = font.style

    # Make axis labels & titles follow the global weight by default
    rcParams["axes.labelweight"] = font.weight
    rcParams["axes.titleweight"] = font.weight

    # TeX / mathtext handling
    rcParams["text.usetex"] = font.use_tex
    if font.use_tex:
        # Preamble (merge user additions). For bold math everywhere, \boldmath helps.
        preamble = font.latex_preamble or ""
        if font.weight.lower() == "bold" and r"\boldmath" not in preamble:
            preamble = (preamble + "\n\\boldmath").strip()
        rcParams["text.latex.preamble"] = preamble
    else:
        # If not using TeX and you want globally bold mathtext too:
        # "bf" makes mathtext bold by default; leave as "regular" otherwise.
        rcParams["mathtext.default"] = "bf" if font.weight.lower() == "bold" else "regular"

@contextmanager
def rc_context(spec):
    # size in inches
    w_in = mm_to_in(spec.size.width) if spec.size.unit == "mm" else (spec.size.width/72.0 if spec.size.unit=="pt" else spec.size.width)
    h_in = mm_to_in(spec.size.height) if spec.size.unit == "mm" else (spec.size.height/72.0 if spec.size.unit=="pt" else spec.size.height)
    old = rcParams.copy()
    try:
        rcParams["figure.figsize"] = [w_in, h_in]
        rcParams["savefig.dpi"] = spec.export.dpi
        rcParams["pdf.fonttype"] = 42
        rcParams["ps.fonttype"] = 42
        _apply_font(spec.font)
        yield
    finally:
        rcParams.update(old)
