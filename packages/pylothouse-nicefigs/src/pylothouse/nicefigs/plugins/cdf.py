import numpy as np
from ..core.layers import Layer
from ..core.utils import resolve_linestyle
from ..core.registry import register

@register("cdf")
class CDFLayer(Layer):
    def draw(self, ax, df):
        x = np.sort(df[self.spec.x].to_numpy())
        y = np.arange(1, len(x)+1) / len(x)
        ax.plot(x, y,
                linewidth=self.spec.style.width,
                linestyle=resolve_linestyle(self.spec.style.style),
                marker=self.spec.style.marker,
                label=self.spec.label_text,
                color=self.spec.style.color)
        ax.set_ylim(0, 1)

@register("ecdf")
class ECDFLayer(CDFLayer):
    pass
