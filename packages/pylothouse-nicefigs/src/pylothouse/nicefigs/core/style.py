from contextlib import contextmanager
from matplotlib import rcParams
from .util import mm_to_in

def _apply_font(font):
    rcParams["font.family"] = font.family
    rcParams["font.size"] = font.size
    rcParams["text.usetex"] = font.use_tex
    if font.use_tex and font.latex_preamble:
        rcParams["text.latex.preamble"] = font.latex_preamble

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
