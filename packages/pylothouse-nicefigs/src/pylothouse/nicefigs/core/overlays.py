"""Utilities for drawing declarative overlays on Matplotlib axes.

This module renders overlay items described by ``OverlaySpec`` into
Matplotlib Artists. It is used by higher-level figure builders to place
consistent annotations and shapes over plots.

Supported overlay types (``OverlaySpec.type``):
- "vline": vertical line at ``x`` in data coordinates.
- "hline": horizontal line at ``y`` in data coordinates.
- "line": line segment between ``(x0, y0)`` and ``(x1, y1)`` in data coordinates.
- "point": scatter marker at ``(x, y)`` (size taken from ``width`` if provided).
- "rect": rectangle specified either by ``(x, y, width, height)`` or by corners
  ``(x0, y0)``–``(x1, y1)`` in data coordinates.
- "circle": circle centered at ``(x, y)`` with ``radius`` in data coordinates.
- "annotation": text placed at ``(x, y)``; returns no artist (draws a Text object).
- "band": vertical band spanning ``[x0, x1]`` in data coordinates and
  ``[ymin_frac, ymax_frac]`` in Axes fraction coordinates (0..1, clamped).

Styling fields (when present) are applied consistently:
- color/facecolor/edgecolor, linewidth, linestyle, alpha, and zorder.
- For filled patches, explicit ``facecolor`` takes precedence over ``color``.
- Legend participation is controlled via ``show_in_legend`` and ``label``.

Error handling: functions fail soft. A malformed spec yields ``None`` (or a
skipped entry), and drawing proceeds for the remaining overlays.
"""

from matplotlib.patches import Rectangle, Circle as MPCircle
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


    """Draw a single overlay element on an Axes.

    This function inspects ``ov.type`` and renders the corresponding Artist on
    ``ax``. It applies styling (color, linewidth, linestyle, alpha, zorder) and
    optionally registers the Artist for legend display when ``ov.show_in_legend``
    is true.

    Args:
        ax: Target Matplotlib ``Axes`` to draw on.
        ov: Overlay specification describing what to draw and how to style it.
        global_font: Reserved for future LaTeX/text styling hooks; currently unused.

    Returns:
        The created Matplotlib Artist for drawable types, or ``None`` if nothing
        was drawn due to missing fields or when the type does not return an
        artist (e.g., "annotation"). Typical return types by overlay:
        - "vline"/"hline": ``matplotlib.lines.Line2D``.
        - "line": ``matplotlib.lines.Line2D`` (from ``Axes.plot``).
        - "point": ``matplotlib.collections.PathCollection`` (from ``Axes.scatter``).
        - "rect": ``matplotlib.patches.Rectangle``.
        - "circle": ``matplotlib.patches.Circle``.
        - "band": ``matplotlib.collections.PolyCollection`` (from ``Axes.axvspan``).
        - "annotation": returns ``None`` (a ``Text`` is still added to the Axes).

    Overlay-specific semantics and required fields (data coordinates unless noted):
        - vline: requires ``x``.
        - hline: requires ``y``.
        - line: requires ``x0, y0, x1, y1``.
        - point: requires ``x, y``; size uses ``width`` if provided (default 30.0).
        - rect: use either ``x, y, width, height`` or ``x0, y0, x1, y1``.
        - circle: requires ``x, y, radius``.
        - annotation: requires ``x, y, text``; offset by ``text_dx, text_dy``; alignment via ``text_align``.
        - band: requires ``x0, x1``; vertical extent defined in Axes fraction via
          ``ymin_frac``/``ymax_frac`` (each clamped to [0, 1]).

    Notes:
        - Patches (rectangles, circles, band) are added to ``ax`` via ``add_patch``
          or the corresponding helper and honor ``facecolor``/``edgecolor``.
        - When both ``color`` and ``facecolor``/``edgecolor`` are present, explicit
          ``facecolor``/``edgecolor`` take precedence.
        - If ``ov.text`` is provided for a rectangle or circle, a centered text
          label is drawn with optional offsets ``text_dx``/``text_dy``.
        - Legend: if ``ov.show_in_legend`` is true, the artist's label is set to
          ``ov.label`` (or "" when None); otherwise any label is cleared.
        - Fail-soft: any exception while drawing this overlay is suppressed and
          results in ``None``.

    Examples:
        >>> art = draw_overlay(ax, OverlaySpec(type='vline', x=0.5, color='k', linestyle='--'))
        >>> art = draw_overlay(ax, OverlaySpec(type='rect', x=0, y=0, width=1, height=2, facecolor='#eee'))
    """
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

    """Draw multiple overlay elements on an Axes.

    Iterates the provided list in order and calls ``draw_overlay`` for each
    ``OverlaySpec``. Any overlay that fails to draw returns ``None`` and is
    skipped; others contribute their created Artist to the return list.

    Args:
        ax: Target Matplotlib ``Axes`` to draw on.
        overlays: Sequence of overlay specifications. ``None`` or empty lists
            are accepted and result in an empty return list.
        global_font: Reserved for future LaTeX/text styling hooks; currently unused.

    Returns:
        List of created Matplotlib Artists (one per overlay that produced an
        artist). Note that overlays of type "annotation" do not return an Artist
        and thus are not included.

    Notes:
        - Overlays are drawn in the order given and honor each spec's ``zorder``.
        - This function never raises for individual spec errors; it aims to be
          robust during batch rendering.
    """

def draw_overlays(ax: Axes, overlays: Optional[List[OverlaySpec]], global_font=None):
    if not overlays:
        return []
    arts = []
    for ov in overlays:
        art = draw_overlay(ax, ov, global_font=global_font)
        if art is not None:
            arts.append(art)
    return arts
