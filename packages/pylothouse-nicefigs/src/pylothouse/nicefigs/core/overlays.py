import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle as MPCircle
from matplotlib.transforms import ScaledTranslation
from typing import List, Optional
from matplotlib.axes import Axes
from ..config.models import OverlaySpec
from .utils import resolve_linestyle

# Helper style applicators

def _apply_line_style(artist, ov: OverlaySpec):
    if ov.color is not None and hasattr(artist, 'set_color'): artist.set_color(ov.color)
    if ov.linewidth is not None and hasattr(artist, 'set_linewidth'): artist.set_linewidth(ov.linewidth)
    if ov.linestyle is not None and hasattr(artist, 'set_linestyle'): artist.set_linestyle(resolve_linestyle(ov.linestyle))
    if ov.alpha is not None and hasattr(artist, 'set_alpha'): artist.set_alpha(ov.alpha)
    if ov.zorder is not None and hasattr(artist, 'set_zorder'): artist.set_zorder(ov.zorder)


def _apply_fill_style(patch, ov: OverlaySpec):
    # precedence: explicit facecolor > color fallback
    if ov.facecolor is not None: patch.set_facecolor(ov.facecolor)
    elif ov.color is not None: patch.set_facecolor(ov.color)
    if ov.edgecolor is not None: patch.set_edgecolor(ov.edgecolor)
    elif ov.color is not None: patch.set_edgecolor(ov.color)
    if ov.alpha is not None: patch.set_alpha(ov.alpha)
    if ov.zorder is not None: patch.set_zorder(ov.zorder)
    if ov.linewidth is not None and hasattr(patch, 'set_linewidth'): patch.set_linewidth(ov.linewidth)
    if ov.linestyle is not None and hasattr(patch, 'set_linestyle'): patch.set_linestyle(resolve_linestyle(ov.linestyle))


def draw_overlay(ax: Axes, ov: OverlaySpec, *, global_font=None):  # global_font kept for future LaTeX styling
    """Draw a single overlay element as specified by OverlaySpec. Returns the created artist or None."""
    t = ov.type
    art = None
    try:
        if t == 'vline':
            if ov.x is None: return None
            art = ax.axvline(ov.x)
            _apply_line_style(art, ov)
        elif t == 'hline':
            if ov.y is None: return None
            art = ax.axhline(ov.y)
            _apply_line_style(art, ov)
        elif t == 'line':  # segment
            if None in (ov.x0, ov.x1, ov.y0, ov.y1): return None
            (art,) = ax.plot([ov.x0, ov.x1], [ov.y0, ov.y1])
            _apply_line_style(art, ov)
        elif t == 'point':
            if None in (ov.x, ov.y): return None
            size = ov.width if ov.width is not None else 30.0  # use width as symbolic size
            art = ax.scatter([ov.x], [ov.y], s=size, c=[ov.color] if ov.color else None)
            if ov.alpha is not None: art.set_alpha(ov.alpha)
            if ov.zorder is not None: art.set_zorder(ov.zorder)
        elif t == 'rect':
            # Prefer (x,y,width,height) else (x0,x1,y0,y1)
            if None not in (ov.x, ov.y, ov.width, ov.height):
                x0, y0, w, h = ov.x, ov.y, ov.width, ov.height
            elif None not in (ov.x0, ov.x1, ov.y0, ov.y1):
                x0, y0 = min(ov.x0, ov.x1), min(ov.y0, ov.y1)
                w = abs(ov.x1 - ov.x0); h = abs(ov.y1 - ov.y0)
            else:
                return None
            art = Rectangle((x0, y0), w, h)
            _apply_fill_style(art, ov)
            ax.add_patch(art)
            if ov.text:
                tx = x0 + w/2.0 + ov.text_dx
                ty = y0 + h/2.0 + ov.text_dy
                ax.text(tx, ty, ov.text, ha=ov.text_align or 'center', va='center',
                        zorder=(ov.zorder + 1 if ov.zorder is not None else None))
        elif t == 'circle':
            if None in (ov.x, ov.y, ov.radius): return None
            art = MPCircle((ov.x, ov.y), radius=ov.radius)
            _apply_fill_style(art, ov)
            ax.add_patch(art)
            if ov.text:
                ax.text(ov.x + ov.text_dx, ov.y + ov.text_dy, ov.text,
                        ha=ov.text_align or 'center', va='center',
                        zorder=(ov.zorder + 1 if ov.zorder is not None else None))
        elif t == 'annotation':
            if None in (ov.x, ov.y, ov.text): return None
            ax.text(ov.x + (ov.text_dx or 0.0), ov.y + (ov.text_dy or 0.0), ov.text,
                    ha=ov.text_align or 'center', va='center', zorder=ov.zorder)
        elif t == 'band':
            if None in (ov.x0, ov.x1): return None
            y0f = 0.0 if ov.ymin_frac is None else max(0.0, min(1.0, ov.ymin_frac))
            y1f = 1.0 if ov.ymax_frac is None else max(0.0, min(1.0, ov.ymax_frac))
            art = ax.axvspan(min(ov.x0, ov.x1), max(ov.x0, ov.x1), ymin=y0f, ymax=y1f,
                              facecolor=ov.facecolor or ov.color, edgecolor=ov.edgecolor,
                              alpha=ov.alpha, linewidth=ov.linewidth,
                              linestyle=resolve_linestyle(ov.linestyle) if ov.linestyle else None,
                              zorder=ov.zorder)
        # Apply label if provided
        if art is not None:
            if ov.show_in_legend:
                try:
                    art.set_label(ov.label if ov.label is not None else "")
                except Exception:
                    pass
            else:
                # ensure no accidental label leaks from defaults
                try:
                    art.set_label(None)
                except Exception:
                    pass
        return art
    except Exception:
        # Fail soft on malformed overlay entry
        return None


def draw_overlays(ax: Axes, overlays: Optional[List[OverlaySpec]], global_font=None):
    if not overlays:
        return []
    arts = []
    for ov in overlays:
        art = draw_overlay(ax, ov, global_font=global_font)
        if art is not None:
            arts.append(art)
    return arts
