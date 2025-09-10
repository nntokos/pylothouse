from typing import Literal
from matplotlib.axes import Axes
import matplotlib.ticker as mticker
from ..config.models import AxesSpec, AxisTicksSpec, TextSpec, TextStyleSpec
import numpy as np
import re

def _as_str_or_empty(x):
    # Treat None (and False, if you like) as an empty label, not "None"
    return "" if x is None else ("" if x is False else str(x))

def _normalize_labels(labels):
    if labels is None:
        return None
    return [_as_str_or_empty(l) for l in labels]

def _merge_text_style(global_font, local):
    """Return canonical matplotlib text property keys inheriting from global font.
    Always include fontfamily, fontsize, fontweight, fontstyle when resolvable.
    """
    fam = (getattr(local, "family", None) if local else None) or getattr(global_font, "family", None)
    siz = (getattr(local, "size", None) if local else None) or getattr(global_font, "size", None)
    wgt = (getattr(local, "weight", None) if local else None) or getattr(global_font, "weight", None)
    sty = (getattr(local, "style", None) if local else None) or getattr(global_font, "style", None)
    col = getattr(local, "color", None) if local else None
    kw = {}
    if fam is not None: kw["fontfamily"] = fam
    if siz is not None: kw["fontsize"] = siz
    if wgt is not None: kw["fontweight"] = wgt
    if sty is not None: kw["fontstyle"] = sty
    if col is not None: kw["color"] = col
    return kw

def _coerce_text_for_setter(text):
    """Return what we should actually pass to Matplotlib setters."""
    if text is None:
        return None  # caller will skip calling the setter
    return "" if text == "" else str(text)

def _latexify_text(s, local_spec, global_font):
    """If using LaTeX and style requests bold/italic, wrap plain text with \\textbf / \\textit.
    Heuristics:
      - Skip if empty, already contains TeX command braces, starts/ends with $...$, or has a backslash (user provided TeX).
      - Nesting handled: bold+italic becomes \\textbf{\\textit{...}}.
    """
    if not s:
        return s
    if not getattr(global_font, "use_tex", False):
        return s
    txt = str(s)
    stripped = txt.strip()
    # Heuristics to avoid double / unwanted wrapping
    if stripped.startswith("$") and stripped.endswith("$"):
        return txt
    if re.search(r"\\text(bf|it)|\\mathbf|\\boldsymbol", txt):
        return txt
    if "\\" in txt:  # user supplied TeX command
        return txt
    weight = (getattr(local_spec, "weight", None) or getattr(global_font, "weight", None) or "").lower()
    style = (getattr(local_spec, "style", None) or getattr(global_font, "style", None) or "").lower()
    wrapped = txt
    if weight == "bold":
        wrapped = f"\\textbf{{{wrapped}}}"
    if style in ("italic", "oblique"):
        # If already bold-wrapped, insert italic inside
        if wrapped.startswith("\\textbf{") and wrapped.endswith("}"):
            inner = wrapped[len("\\textbf{"):-1]
            if not inner.startswith("\\textit{"):
                inner = f"\\textit{{{inner}}}"
            wrapped = f"\\textbf{{{inner}}}"
        else:
            wrapped = f"\\textit{{{wrapped}}}"
    return wrapped

def _apply_text_spec(setter, artist_getter, spec, global_font, *, pad_kw=None, align_key=None):
    if not spec or not getattr(spec, "show", True):
        # hide if possible
        artist = artist_getter()
        if artist is not None:
            artist.set_visible(False)
        return

    text_val = _coerce_text_for_setter(getattr(spec, "text", None))
    kw = _merge_text_style(global_font, spec)
    # adapt alignment/padding
    if pad_kw and getattr(spec, "pad", None) is not None:
        kw[pad_kw] = spec.pad
    if align_key and getattr(spec, "ha", None) is not None:
        kw[align_key] = spec.ha

    # Only call the setter when we have a concrete string; skip if None
    if text_val is not None:
        # LaTeX wrapping
        if text_val != "" and getattr(global_font, "use_tex", False):
            text_val = _latexify_text(text_val, spec, global_font)
        setter(text_val, **kw)
    else:
        # still apply style to existing text if you want:
        existing = artist_getter().get_text()
        if getattr(global_font, "use_tex", False):
            existing = _latexify_text(existing, spec, global_font)
        setter(existing, **kw)

    artist = artist_getter()
    if artist is not None and getattr(spec, "rotation", None) is not None:
        artist.set_rotation(spec.rotation)
    if artist is not None:
        artist.set_visible(True)

def _apply_spines(ax: Axes, sp):
    spines = ax.spines
    spines["left"].set_visible(sp.show_left)
    spines["right"].set_visible(sp.show_right)
    spines["top"].set_visible(sp.show_top)
    spines["bottom"].set_visible(sp.show_bottom)
    if sp.color is not None or sp.linewidth is not None:
        for key in ["left","right","top","bottom"]:
            if sp.color is not None:    spines[key].set_edgecolor(sp.color)
            if sp.linewidth is not None: spines[key].set_linewidth(sp.linewidth)

def _apply_axis_ticks(ax: Axes, axis_name: Literal["x","y"], ticks_spec: AxisTicksSpec, global_font):
    # Apply tick label style and tick mark styling/placement/formatting.
    axis = ax.xaxis if axis_name == "x" else ax.yaxis
    if not ticks_spec or not getattr(ticks_spec, "show", True):
        return

    # ---- 1) Placement
    if getattr(ticks_spec, "locations", None) is not None:
        set_ticks = ax.set_xticks if axis_name == "x" else ax.set_yticks
        set_ticks(ticks_spec.locations)
        if getattr(ticks_spec, "labels", None) is not None:
            plain = [
                (lbl.text if isinstance(lbl, TextSpec) else ("" if lbl is None else str(lbl)))
                for lbl in ticks_spec.labels
            ]
            if getattr(global_font, "use_tex", False):
                latex_plain = [
                    _latexify_text(p, lbl if isinstance(lbl, TextSpec) else ticks_spec, global_font) if p else p
                    for p, lbl in zip(plain, ticks_spec.labels)
                ]
                (ax.xaxis if axis_name == "x" else ax.yaxis).set_ticklabels(latex_plain)
            else:
                (ax.xaxis if axis_name == "x" else ax.yaxis).set_ticklabels(plain)
    elif getattr(ticks_spec, "range", None) is not None and len(ticks_spec.range) == 3:
        lo, hi, step = ticks_spec.range
        # be inclusive with small epsilon to avoid fp drift
        eps = abs(step) * 1e-9
        locs = list(np.arange(lo, hi + eps, step))
        (ax.set_xticks if axis_name == "x" else ax.set_yticks)(locs)

    # ---- 2) tick_params for marks
    which = getattr(ticks_spec, "which", "major")
    style_kw = _merge_text_style(global_font, ticks_spec)
    tick_kw = {}
    # Tick mark styling
    if getattr(ticks_spec, "direction", None) is not None: tick_kw["direction"] = ticks_spec.direction
    if getattr(ticks_spec, "length", None)    is not None: tick_kw["length"]    = ticks_spec.length
    if getattr(ticks_spec, "width", None)     is not None: tick_kw["width"]     = ticks_spec.width
    if getattr(ticks_spec, "color", None)     is not None: tick_kw["color"]     = ticks_spec.color
    if "fontsize" in style_kw: tick_kw["labelsize"]  = style_kw["fontsize"]
    if "color"    in style_kw: tick_kw["labelcolor"] = style_kw["color"]
    if getattr(ticks_spec, "rotation", None) is not None:
        tick_kw["labelrotation"] = ticks_spec.rotation

    if tick_kw:
        ax.tick_params(axis=axis_name, which=which, **tick_kw)

    # ---- 3) Per-label overrides (family/weight/style not supported by tick_params)
    #      Do this AFTER tick_params so we win any tie.
    labels_major = (ax.xaxis if axis_name=="x" else ax.yaxis).get_ticklabels(minor=False)
    labels_minor = (ax.xaxis if axis_name=="x" else ax.yaxis).get_ticklabels(minor=True)
    label_sets = []
    if which in ("major","both"): label_sets.append(labels_major)
    if which in ("minor","both"): label_sets.append(labels_minor)

    for labels in label_sets:
        for lab in labels:
            # Only apply properties tick_params cannot handle (family/weight/style).
            if "fontfamily" in style_kw: lab.set_family(style_kw["fontfamily"])
            if "fontweight" in style_kw: lab.set_weight(style_kw["fontweight"])
            if "fontstyle"  in style_kw: lab.set_style(style_kw["fontstyle"])
            # size and color already applied via tick_params; skip redundant set_size/set_color
            if getattr(ticks_spec, "rotation", None) is not None:
                lab.set_rotation(ticks_spec.rotation)
                if hasattr(lab, "set_rotation_mode"): lab.set_rotation_mode("anchor")

    # ---- 4) Formatting
    fmt = getattr(ticks_spec, "fmt", None)
    if fmt is not None:
        if callable(fmt):
            def _f(v, p):
                base = _as_str_or_empty(fmt(v, p))
                return _latexify_text(base, ticks_spec, global_font)
            formatter = mticker.FuncFormatter(lambda v, p: _f(v, p))
        elif isinstance(fmt, str) and fmt == "":
            formatter = mticker.FuncFormatter(lambda v, p: "")
        elif isinstance(fmt, str) and "%" in fmt:
            def _f(v, p):
                base = (fmt % v)
                return _latexify_text(base, ticks_spec, global_font)
            formatter = mticker.FuncFormatter(lambda v, p: _f(v, p))
        elif isinstance(fmt, str):
            def _f(v, p):
                try:
                    base = fmt.format(v)
                except Exception:
                    base = str(v)
                return _latexify_text(base, ticks_spec, global_font)
            formatter = mticker.FuncFormatter(lambda v, p: _f(v, p))
        else:
            formatter = None
        if formatter is not None:
            (ax.xaxis if axis_name == "x" else ax.yaxis).set_major_formatter(formatter)

    # Post-format LaTeX pass to any existing tick labels (avoid double wrap)
    if getattr(global_font, "use_tex", False):
        labels_major = (ax.xaxis if axis_name=="x" else ax.yaxis).get_ticklabels(minor=False)
        labels_minor = (ax.xaxis if axis_name=="x" else ax.yaxis).get_ticklabels(minor=True)
        to_process = []
        which = getattr(ticks_spec, "which", "major")
        if which in ("major","both"): to_process.extend(labels_major)
        if which in ("minor","both"): to_process.extend(labels_minor)
        for lab in to_process:
            t = lab.get_text()
            if t:
                lab.set_text(_latexify_text(t, ticks_spec, global_font))

    # ---- 5) Explicit per-label TextSpec after global style
    if getattr(ticks_spec, "labels", None) is not None:
        tick_texts = (ax.xaxis if axis_name == "x" else ax.yaxis).get_ticklabels()
        for i, lbl_spec in enumerate(ticks_spec.labels):
            if i >= len(tick_texts):
                break
            if isinstance(lbl_spec, TextSpec):
                tt = tick_texts[i]
                if lbl_spec.family: tt.set_family(lbl_spec.family)
                if lbl_spec.size: tt.set_size(lbl_spec.size)
                if lbl_spec.weight: tt.set_weight(lbl_spec.weight)
                if lbl_spec.style: tt.set_style(lbl_spec.style)
                if lbl_spec.color: tt.set_color(lbl_spec.color)
                if lbl_spec.rotation is not None: tt.set_rotation(lbl_spec.rotation)
                if getattr(global_font, "use_tex", False):
                    tt.set_text(_latexify_text(tt.get_text(), lbl_spec, global_font))

def setup_axes(ax: Axes, axes_spec: AxesSpec, global_font):
    # scales
    ax.set_xscale(axes_spec.xscale)
    ax.set_yscale(axes_spec.yscale)

    # title
    _apply_text_spec(ax.set_title, lambda: ax.title, axes_spec.title, global_font, pad_kw="pad", align_key="loc")

    # x/y labels
    _apply_text_spec(ax.set_xlabel, lambda: ax.xaxis.label, axes_spec.xlabel, global_font, pad_kw="labelpad")
    _apply_text_spec(ax.set_ylabel, lambda: ax.yaxis.label, axes_spec.ylabel, global_font, pad_kw="labelpad")

    # grid
    if axes_spec.grid.show:
        ax.grid(True, which=axes_spec.grid.which,
                linestyle=axes_spec.grid.linestyle,
                linewidth=axes_spec.grid.linewidth,
                color=axes_spec.grid.color)
    else:
        ax.grid(False)

    # limits
    lims = axes_spec.limits
    if lims.get("x"): ax.set_xlim(*lims["x"])
    if lims.get("y"): ax.set_ylim(*lims["y"])

    # ticks & spines
    _apply_axis_ticks(ax, "x", axes_spec.xticks, global_font)
    _apply_axis_ticks(ax, "y", axes_spec.yticks, global_font)
    _apply_spines(ax, axes_spec.spines)

    # optional: hide whole axes frame (keeps data/labels if you want)
    if not axes_spec.show_axes_frame:
        for key in ["left","right","top","bottom"]:
            ax.spines[key].set_visible(False)

    return ax

def maybe_legend(ax: Axes, legend_spec, global_font):
    if not legend_spec.show:
        leg = ax.get_legend()
        if leg: leg.remove()
        return

    user_label_specs = legend_spec.labels
    handles_all, labels_all = ax.get_legend_handles_labels()
    filtered = [(h, l) for h, l in zip(handles_all, labels_all) if l and not l.startswith('_')]

    if user_label_specs is not None:
        base_handles = [h for h, _ in filtered]
        need = len(user_label_specs)
        if len(base_handles) < need:
            from matplotlib.lines import Line2D
            base_handles += [Line2D([0],[0], color='black') for _ in range(need - len(base_handles))]
        handles = base_handles[:need]
        labels = [(ls.text if isinstance(ls, TextSpec) else ("" if ls is None else str(ls))) for ls in user_label_specs]
    else:
        if filtered:
            handles, labels = zip(*filtered)
        else:
            lines = [ln for ln in ax.get_lines() if ln.get_visible()]
            artists = lines or [p for p in ax.patches if p.get_visible()]
            if not artists: return
            handles = artists
            labels = [f"Series {i+1}" for i,_ in enumerate(artists)]

    # LaTeXify labels before legend creation
    if getattr(global_font, "use_tex", False):
        latex_labels = []
        for idx, lbl in enumerate(labels):
            spec_for = user_label_specs[idx] if (user_label_specs and idx < len(user_label_specs) and isinstance(user_label_specs[idx], TextSpec)) else legend_spec.style
            latex_labels.append(_latexify_text(lbl, spec_for if spec_for else legend_spec.style, global_font))
        labels = latex_labels

    title_spec = legend_spec.title if isinstance(legend_spec.title, TextSpec) else None
    title_text = title_spec.text if title_spec else (legend_spec.title if legend_spec.title else "Legend")
    if getattr(global_font, "use_tex", False):
        title_text = _latexify_text(title_text, title_spec or legend_spec.style or TextStyleSpec(), global_font)

    leg = ax.legend(handles, labels, loc=legend_spec.loc, ncol=legend_spec.ncol,
                    frameon=legend_spec.frameon, title=title_text)
    if leg is None:
        return

    # Only ensure LaTeX wrapping remains; no redundant style reapplication.
    if getattr(global_font, "use_tex", False):
        for idx, txt_obj in enumerate(leg.get_texts()):
            spec_for = None
            if user_label_specs and idx < len(user_label_specs) and isinstance(user_label_specs[idx], TextSpec):
                spec_for = user_label_specs[idx]
            txt_obj.set_text(_latexify_text(txt_obj.get_text(), spec_for or legend_spec.style or TextStyleSpec(), global_font))

        lt = leg.get_title()
        if lt:
            lt.set_text(_latexify_text(lt.get_text(), title_spec or legend_spec.style or TextStyleSpec(), global_font))
    return leg
