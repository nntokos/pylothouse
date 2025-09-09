from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal

Unit = float

class Size(BaseModel):
    width: Unit
    height: Unit
    unit: Literal["mm","in","pt"] = "in"

class FontSpec(BaseModel):
    family: str = "serif"
    size: int = 9
    use_tex: bool = True
    latex_preamble: Optional[str] = r"\usepackage{amsmath}"

class LineSpec(BaseModel):
    color: Optional[str] = None
    width: float = 1.0
    style: Literal["solid","dashed","dotted","dashdot"] = "solid"
    marker: Optional[str] = None

class LegendSpec(BaseModel):
    show: bool = True
    loc: str = "best"
    ncol: int = 1
    frameon: bool = False

class AxesSpec(BaseModel):
    title: Optional[str] = None
    xlabel: Optional[str] = None
    ylabel: Optional[str] = None
    xscale: Literal["linear","log","symlog"] = "linear"
    yscale: Literal["linear","log","symlog"] = "linear"
    grid: bool = True
    limits: Dict[str, Optional[List[float]]] = Field(default_factory=lambda: {"x": None, "y": None})
    legend: LegendSpec = LegendSpec()

class SeriesSpec(BaseModel):
    type: Literal["line","scatter","bar","hist","cdf","ecdf","heatmap"]
    x: Optional[str] = None
    y: Optional[str] = None
    data: Optional[str] = None
    query: Optional[str] = None
    style: LineSpec = LineSpec()
    label: Optional[str] = None
    bins: Optional[int] = None  # for hist

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
    # Absolute directory containing the loaded YAML config; used for resolving relative paths.
    base_dir: Optional[str] = None
