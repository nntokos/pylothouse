from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Literal, Union
from pydantic import field_validator
from pydantic import model_validator

Unit = float

# Base text style and TextLike definitions (single source)
class TextStyleSpec(BaseModel):
    family: Optional[str] = None
    size: Optional[float] = None
    weight: Optional[str] = None
    style: Optional[str] = None
    color: str = "black"

class TextSpec(TextStyleSpec):
    show: bool = True
    text: Optional[str] = None
    rotation: Optional[float] = None
    ha: Optional[str] = None
    va: Optional[str] = None
    pad: Optional[float] = None

TextLike = Union[str, TextSpec, None]

class Size(BaseModel):
    width: Unit
    height: Unit
    unit: Literal["mm","in","pt"] = "in"

class FontSpec(BaseModel):
    family: str = "serif"
    size: int = 9
    weight: str = "normal"  # ("normal", "bold", "light", …)
    style: str = "normal"  # ("normal", "italic", "oblique")
    use_tex: bool = True
    latex_preamble: Optional[str] = r"\usepackage{amsmath}"

class TickFormatterSpec(BaseModel):
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
    show: bool = True                  # show/hide tick labels
    rotation: Optional[float] = None   # unified rotation (replaces legacy label_rotation)
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

    # global visibility switches for “everything removable”
    show_axes_frame: bool = True   # outline/spines toggles tie into SpinesSpec
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
    show: bool = True
    loc: str = "best"
    ncol: int = 1
    frameon: bool = False
    title: TextLike = None
    labels: Optional[List[TextLike]] = None
    style: Optional[TextStyleSpec] = None   # global legend text style fallback

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
    show: bool = True
    which: str = "both"          # "major","minor","both"
    linestyle: str = ":"         # ":", "--", "-", ...
    linewidth: float = 0.5
    color: str = "#cccccc"

class SpinesSpec(BaseModel):
    show_left: bool = True
    show_right: bool = True
    show_top: bool = True
    show_bottom: bool = True
    color: str = "black"
    linewidth: Optional[float] = None

class LineSpec(BaseModel):
    color: str = "C0"
    width: float = 1.0
    style: Literal["solid","dashed","dotted","dashdot"] = "solid"
    marker: Optional[str] = None

class SeriesSpec(BaseModel):
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
        if self.label is None: return None
        if isinstance(self.label, TextSpec):
            return self.label.text
        return str(self.label)

class PanelSpec(BaseModel):
    axes: AxesSpec = AxesSpec()
    series: List[SeriesSpec] = Field(default_factory=list)

class LayoutSpec(BaseModel):
    rows: int = 1
    cols: int = 1
    wspace: float = 0.1
    hspace: float = 0.1
    shared_x: bool = False
    shared_y: bool = False

class ExportSpec(BaseModel):
    path: str = "figure.png"
    dpi: int = 300
    formats: List[Literal["pdf","png","svg"]] = ["png"]
    tight_layout: bool = True
    metadata: Dict[str, str] = Field(default_factory=dict)

class FigureSpec(BaseModel):
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
