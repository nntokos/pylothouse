"""
Pydantic models for nicefigs configuration.

This module defines the full, declarative schema used to configure figures,
axes, typography, legends, tick formatting, overlays (extra shapes/annotations),
layout, and export behavior. These classes are validated via Pydantic and are
typically constructed from a YAML file (see loader.load_config) or from Python
code. The loader also expands overlay file references before validation.

Conventions and units
- Figure/size units: controlled by FigureSpec.size.unit ("in", "mm", or "pt").
- Text offsets (dx/dy):
  - dx_unit/dy_unit = "points": values are absolute and interpreted in the
    figure size unit; they are converted to display space and applied as a
    translation transform.
  - dx_unit/dy_unit = "axes": values are in data units and converted to a
    relative deflection based on the current axis x/y range and axes bounding
    box dimensions.
- Legend offsets: offset_unit behaves similarly ("axes" vs "points").
- Linestyles: several aliases (solid, dashed, dotted, dashdot or their symbol
  forms) are normalized internally.
- Overlays: panel.overlays may contain inline overlay objects or file paths;
  the loader expands file paths into inline dicts prior to validation.

The API favors minimal surprises: unspecified attributes adopt sensible
defaults; validators coerce common shorthands (e.g. strings into TextSpec).
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional, Dict, Literal, Union

Unit = float

# Base text style and TextLike definitions (single source)
class TextStyleSpec(BaseModel):
    """Base typographic properties shared by all text-bearing specs.

    Fields
    - family: Font family name (e.g., "serif", "sans-serif", "Times New Roman").
    - size: Font size in points.
    - weight: Weight string (e.g., "normal", "bold").
    - style: Style string ("normal", "italic", "oblique").
    - color: Text color (any Matplotlib color spec).
    """
    family: Optional[str] = None
    size: Optional[float] = None
    weight: Optional[str] = None
    style: Optional[str] = None
    color: str = "black"

class TextSpec(TextStyleSpec):
    """Concrete text content and presentation for labels, titles, etc.

    Fields
    - show: Toggle visibility.
    - text: The text content; None means "leave as-is", empty string means
      explicitly render no text ("").
    - rotation: Rotation angle in degrees.
    - ha / va: Horizontal/vertical alignment (Matplotlib keywords).
    - pad: Extra padding in points when supported by the target setter.
    - dx / dy: Positional offset applied after drawing (see units below).
    - dx_unit / dy_unit:
        - "points": absolute offset interpreted using FigureSpec.size.unit
          (in/mm/pt) and converted to display space.
        - "axes": data-unit deflection converted relative to the current axis
          range and the axes bounding box.
    """
    show: bool = True
    text: Optional[str] = None
    rotation: Optional[float] = None
    ha: Optional[str] = None
    va: Optional[str] = None
    pad: Optional[float] = None
    dx: Optional[float] = None   # horizontal offset
    dy: Optional[float] = None   # vertical offset
    dx_unit: Literal["axes","points"] = "axes"
    dy_unit: Literal["axes","points"] = "axes"

TextLike = Union[str, TextSpec, None]

class Size(BaseModel):
    """Canvas size for the exported figure.

    Fields
    - width / height: Dimensions in unit.
    - unit: One of {"in", "mm", "pt"}.
    """
    width: Unit
    height: Unit
    unit: Literal["mm","in","pt"] = "in"

class FontSpec(BaseModel):
    """Global default font settings applied to the figure.

    Fields
    - family, size, weight, style: Standard font parameters.
    - use_tex: If true, Matplotlib uses LaTeX for text rendering.
    - latex_preamble: Additional LaTeX preamble inserted when use_tex=True.
    """
    family: str = "serif"
    size: int = 9
    weight: str = "normal"  # ("normal", "bold", "light", …)
    style: str = "normal"  # ("normal", "italic", "oblique")
    use_tex: bool = True
    latex_preamble: Optional[str] = r"\usepackage{amsmath}"

class TickFormatterSpec(BaseModel):
    """Declarative tick formatter configuration (extensible).

    Fields
    - kind: Formatter family ("printf", "strfmt", "sci", "eng", "percent",
      "thousands", "si", "date", "custom").
    - pattern / unit / places / scale / prefix / suffix: Optional parameters
      used by specific formatter kinds.
    - wrap_mathtext, bold, italic: Optional mathtext styling flags.
    - expression: Optional expression for custom formatters.
    Note: not all options may be used by the current implementation yet.
    """
    kind: Literal["printf","strfmt","sci","eng","percent","thousands","si","date","custom"] = "strfmt"
    pattern: Optional[str] = None
    sci_limits: Optional[List[int]] = None
    unit: Optional[str] = None
    places: Optional[int] = None
    scale: Optional[float] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    use_mathtext: Optional[bool] = None
    expression: Optional[str] = None
    # optional mathtext wrappers
    wrap_mathtext: bool = False        # if true, surround with $...$
    bold: bool = False                 # if true, wrap with \mathbf{...}
    italic: bool = False               # if true, wrap with \mathit{...}

class AxisTicksSpec(TextStyleSpec):
    """Styling and placement of axis tick marks and labels.

    Fields
    - show: Toggle label visibility (tick marks still follow Matplotlib defaults).
    - rotation: Label rotation (degrees).
    - direction: Tick direction ("in", "out", "inout").
    - length / width / color: Tick mark style.
    - locations: Explicit tick locations (list of floats).
    - range: Convenience spec [min, max, step] to generate ticks (inclusive).
    - fmt: Optional tick formatter spec (see TickFormatterSpec).
    - labels: Optional per-tick label overrides. Each entry may be:
        * None: keep existing
        * str: coerced into TextSpec(text=str)
        * TextSpec: full control per label
    """
    show: bool = True                  # show/hide tick labels
    rotation: Optional[float] = None   # unified rotation
    direction: Optional[str] = None    # "in", "out", "inout"
    length: Optional[float] = None
    width: Optional[float] = None
    locations: Optional[List[float]] = None
    range: Optional[List[float]] = None  # [min,max,step]
    fmt: Optional[TickFormatterSpec] = None
    labels: Optional[List[TextLike]] = None

    @field_validator("labels", mode="before")
    @classmethod
    def _coerce_tick_labels(cls, v):
        if v is None: return None
        if not isinstance(v, list):
            raise TypeError("axes.*ticks.labels must be a list")
        out = []
        for item in v:
            if item is None:
                out.append(None)
            elif isinstance(item, TextSpec):
                out.append(item)
            elif isinstance(item, str):
                out.append(TextSpec(text=item))
            elif isinstance(item, dict):
                out.append(TextSpec.model_validate(item))
            else:
                raise TypeError("tick label entries must be str | TextSpec | dict | None")
        return out

class AxesSpec(BaseModel):
    """All per-axes visual and layout configuration.

    Fields
    - title / xlabel / ylabel: TextLike for axis texts.
    - xscale / yscale: Scale names ("linear", "log", "symlog").
    - grid: GridSpec for background grid configuration.
    - limits: dict with keys "x" and/or "y"; values [min, max].
    - legend: LegendSpec for legend settings.
    - spines: SpinesSpec to toggle sides and set style.
    - xticks / yticks: AxisTicksSpec for tick styling & placement.
    - show_axes_frame: If false, hides all spines.
    - show_xlabel / show_ylabel / show_title: Global visibility toggles.
    """
    model_config = ConfigDict(validate_assignment=True)
    title: TextLike = None
    xlabel: TextLike = None
    ylabel: TextLike = None
    xscale: Literal["linear","log","symlog"] = "linear"
    yscale: Literal["linear","log","symlog"] = "linear"
    grid: "GridSpec" = Field(default_factory=lambda: GridSpec())
    limits: Dict[str, Optional[List[float]]] = Field(default_factory=lambda: {"x": None, "y": None})
    legend: "LegendSpec" = Field(default_factory=lambda: LegendSpec())
    spines: "SpinesSpec" = Field(default_factory=lambda: SpinesSpec())
    xticks: AxisTicksSpec = Field(default_factory=lambda: AxisTicksSpec())
    yticks: AxisTicksSpec = Field(default_factory=lambda: AxisTicksSpec())

    # global visibility switches
    show_axes_frame: bool = True
    show_xlabel: bool = True
    show_ylabel: bool = True
    show_title: bool = True

    @field_validator("title", "xlabel", "ylabel", mode="before")
    @classmethod
    def _coerce_text_like(cls, v):
        if v is None: return None
        if isinstance(v, TextSpec): return v
        if isinstance(v, str): return TextSpec(text=v)
        if isinstance(v, dict): return TextSpec.model_validate(v)
        raise TypeError("title/xlabel/ylabel must be str | TextSpec | dict | None")

class LegendSpec(BaseModel):
    """Legend placement and styling options.

    Fields
    - show: Toggle legend visibility.
    - loc: Matplotlib legend location string (e.g., "best", "upper right").
    - ncol: Number of columns.
    - frameon: Draw a frame around the legend.
    - title: Optional legend title (TextLike).
    - labels: Optional list of TextLike to override legend entry texts.
    - style: Global text style defaults (merged with per-label overrides).
    - anchor: Optional bbox_to_anchor list [x, y] or [x, y, w, h] in axes coords.
    - offset_x / offset_y: Additional offset applied to anchor.
    - offset_unit: "axes" uses axes fractions; "points" are absolute points.
    """
    show: bool = True
    loc: str = "best"
    ncol: int = 1
    frameon: bool = False
    title: TextLike = None
    labels: Optional[List[TextLike]] = None
    style: Optional[TextStyleSpec] = None   # global legend text style fallback
    anchor: Optional[List[float]] = None    # base bbox_to_anchor [x,y] or [x,y,w,h]
    offset_x: Optional[float] = None        # shift applied to anchor/transform x
    offset_y: Optional[float] = None        # shift applied to anchor/transform y
    offset_unit: Literal["axes","points"] = "axes"

    @field_validator("title", mode="before")
    @classmethod
    def _coerce_title(cls, v):
        if v is None: return None
        if isinstance(v, TextSpec): return v
        if isinstance(v, str): return TextSpec(text=v)
        if isinstance(v, dict): return TextSpec.model_validate(v)
        raise TypeError("legend.title must be str | TextSpec | dict | None")

    @field_validator("labels", mode="before")
    @classmethod
    def _coerce_labels(cls, v):
        if v is None: return None
        if not isinstance(v, list):
            raise TypeError("legend.labels must be a list")
        out = []
        for item in v:
            if item is None:
                out.append(None)
            elif isinstance(item, TextSpec):
                out.append(item)
            elif isinstance(item, str):
                out.append(TextSpec(text=item))
            elif isinstance(item, dict):
                out.append(TextSpec.model_validate(item))
            else:
                raise TypeError("legend.labels entries must be str | TextSpec | dict | None")
        return out

class GridSpec(BaseModel):
    """Background grid settings for an axes.

    Fields
    - show: Toggle grid visibility.
    - which: Grid on "major", "minor", or "both" ticks.
    - linestyle / linewidth / color: Style of grid lines.
    """
    show: bool = True
    which: Literal["major","minor","both"] = "both"
    linestyle: str = ":"
    linewidth: float = 0.5
    color: str = "#cccccc"

class SpinesSpec(BaseModel):
    """Visibility and styling for the four axes spines (borders)."""
    show_left: bool = True
    show_right: bool = True
    show_top: bool = True
    show_bottom: bool = True
    color: str = "black"
    linewidth: Optional[float] = None

class LineSpec(BaseModel):
    """Per-series line/marker styling.

    Fields
    - color: Line or marker color.
    - width: Line width in points.
    - style: Normalized line style ("solid", "dashed", "dotted", "dashdot").
    - marker: Optional marker symbol for scatter/line.
    """
    color: str = "C0"
    width: float = 1.0
    style: Literal["solid","dashed","dotted","dashdot"] = "solid"
    marker: Optional[str] = None

class SeriesSpec(BaseModel):
    """A single data series and how to render it.

    Fields
    - type: One of {"line", "scatter", "bar", "hist", "cdf", "ecdf", "heatmap"}.
    - x / y: Column names (or keys) in the loaded DataFrame.
    - data: Data source reference (path/URL/callable/DF), resolved by readers.
    - query: Optional pandas query string to filter the DataFrame.
    - style: See LineSpec.
    - label: Legend label (TextLike); coerced to TextSpec.
    - bins: Number of bins (hist only).
    """
    type: Literal["line","scatter","bar","hist","cdf","ecdf","heatmap"]
    x: Optional[str] = None
    y: Optional[str] = None
    data: Optional[str] = None
    query: Optional[str] = None
    style: LineSpec = LineSpec()
    label: TextLike = None
    bins: Optional[int] = None  # for hist

    @field_validator("label", mode="before")
    @classmethod
    def _coerce_label(cls, v):
        if v is None: return None
        if isinstance(v, TextSpec): return v
        if isinstance(v, str): return TextSpec(text=v)
        if isinstance(v, dict): return TextSpec.model_validate(v)
        raise TypeError("series.label must be str | TextSpec | dict | None")

    @property
    def label_text(self) -> Optional[str]:
        """Convenience for Matplotlib label argument: returns concrete string or None."""
        if self.label is None: return None
        if isinstance(self.label, TextSpec):
            return self.label.text
        return str(self.label)

# Overlay specification (simple, generic)
class OverlaySpec(BaseModel):
    """Extra visual components drawn on top of the data.

    Supported types
    - vline / hline: vertical or horizontal line at x or y.
    - line: generic segment from (x0, y0) to (x1, y1).
    - point: a point at (x, y); "width" is used as marker size fallback.
    - rect: rectangle defined by (x, y, width, height) or by corners (x0, x1, y0, y1).
    - circle: center (x, y) with data-unit radius.
    - annotation: free text placed at (x, y) with optional offsets (`text_dx`/`text_dy`),
      rotation in degrees (`text_rotation`), and text alignment (`text_ha`/`text_va`).
    - band: vertical band between x0 and x1 with vertical extent in axis fractions
      [ymin_frac, ymax_frac].

    Common style fields
    - color, edgecolor, facecolor, alpha, linewidth, linestyle, zorder

    Legend behavior
    - show_in_legend: if true, the overlay is added to the legend; if label is
      None, an empty label is used to reserve a slot.
    """
    type: Literal["line","hline","vline","point","rect","circle","annotation","band"]
    color: Optional[str] = None
    edgecolor: Optional[str] = None
    facecolor: Optional[str] = None
    fill: Optional[bool] = None
    alpha: Optional[float] = None
    linewidth: Optional[float] = None
    linestyle: Optional[str] = None
    label: Optional[str] = None
    show_in_legend: bool = False  # new flag to force legend inclusion
    zorder: Optional[int] = None
    # geometry
    x: Optional[float] = None
    y: Optional[float] = None
    x0: Optional[float] = None
    x1: Optional[float] = None
    y0: Optional[float] = None
    y1: Optional[float] = None
    radius: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    # text / annotation
    text: Optional[str] = None
    text_dx: float = 0.0
    text_dy: float = 0.0
    # New: explicit horizontal/vertical alignment for overlay text
    text_ha: Optional[str] = None  # e.g., 'left' | 'center' | 'right'
    text_va: Optional[str] = None  # e.g., 'top' | 'center' | 'bottom' | 'baseline'
    text_rotation: Optional[float] = None  # degrees
    ymin_frac: Optional[float] = None
    ymax_frac: Optional[float] = None

OverlayLike = Union[OverlaySpec, str]

class PanelSpec(BaseModel):
    """A single panel (subplot) containing series and optional overlays.

    Fields
    - axes: AxesSpec with all per-axes styling and text.
    - series: List of SeriesSpec to draw on this axes.
    - overlays: List of OverlaySpec or file paths (strings). File paths are
      expanded into inline overlay dicts by the loader before validation.
    """
    axes: AxesSpec = AxesSpec()
    series: List[SeriesSpec] = Field(default_factory=list)
    overlays: Optional[List[OverlayLike]] = None  # file path strings expanded in loader BEFORE validation

    @field_validator("overlays", mode="before")
    @classmethod
    def _coerce_overlays(cls, v):
        if v is None:
            return None
        if not isinstance(v, list):
            raise TypeError("panel.overlays must be a list")
        out = []
        for item in v:
            if item is None:
                continue
            if isinstance(item, OverlaySpec):
                out.append(item)
            elif isinstance(item, str):  # file path kept for loader phase already expanded; treat as error if still present
                # If a file path string reached here, expansion was skipped; raise to surface configuration issue.
                raise ValueError("Overlay file paths must be expanded before validation (loader should replace them with dict entries).")
            elif isinstance(item, dict):
                out.append(OverlaySpec.model_validate(item))
            else:
                raise TypeError("overlay list entries must be dict or OverlaySpec after loader expansion")
        return out

class LayoutSpec(BaseModel):
    """Grid layout for all panels in the figure.

    Fields
    - rows / cols: Grid dimensions.
    - wspace / hspace: Spacing between subplots. If either is None, automatic
      spacing is applied via constrained_layout, with optional partial overrides
      if one of the two is provided.
    - shared_x / shared_y: Share axes among subplots.
    """
    rows: int = 1
    cols: int = 1
    wspace: Optional[float] = None   # None => auto spacing
    hspace: Optional[float] = None   # None => auto spacing
    shared_x: bool = False
    shared_y: bool = False

class ExportSpec(BaseModel):
    """Export options for saving the figure.

    Fields
    - path: Output path (directory may be relative to YAML file location).
    - dpi: Rasterization DPI (applies to png).
    - formats: One or more of {"png", "pdf", "svg"}.
    - tight_layout: If true, applies Matplotlib tight layout before saving.
    - metadata: Optional export metadata dict.
    """
    path: str = "figure.png"
    dpi: int = 300
    formats: List[Literal["pdf","png","svg"]] = ["png"]
    tight_layout: bool = True
    metadata: Dict[str, str] = Field(default_factory=dict)

class FigureSpec(BaseModel):
    """Top-level figure specification containing panels and defaults.

    Fields
    - size: Figure canvas dimensions/units.
    - font: Global font defaults (merged into all text unless overridden).
    - layout: Grid layout with spacing semantics (see LayoutSpec).
    - panels: Ordered list of PanelSpec. If fewer than rows*cols, remaining
      axes are removed so empty panels are not shown.
    - theme / preset: Optional helpers to apply predefined styling.
    - palette: Optional categorical palette name.
    - export: Export instruction bundle.
    - axes_defaults: Optional AxesSpec applied to every panel then overridden
      by the panel-specific axes.
    - base_dir: Absolute directory of the loaded YAML; set by the loader and
      used for resolving relative paths (including overlay files).
    """
    size: Size
    font: FontSpec = FontSpec()
    layout: LayoutSpec = LayoutSpec()
    panels: List[PanelSpec]
    theme: Optional[str] = None
    preset: Optional[str] = None
    palette: Optional[str] = "okabe_ito"
    export: ExportSpec = ExportSpec()
    # Optional default axes styling applied to each panel then overridden by panel.axes
    axes_defaults: Optional[AxesSpec] = None
    # Absolute directory containing the loaded YAML config; used for resolving relative paths.
    base_dir: Optional[str] = None
