import numpy as np
from ..core.layers import Layer, _to_linestyle
from ..core.registry import register

@register("cdf")
class CDFLayer(Layer):
    def draw(self, ax, df):
        x = np.sort(df[self.spec.x].to_numpy())
        y = np.arange(1, len(x)+1) / len(x)
        ax.plot(x, y,
                linewidth=self.spec.style.width,
                linestyle=_to_linestyle(self.spec.style.style),
                marker=self.spec.style.marker,
                label=self.spec.label,
                color=self.spec.style.color)
        ax.set_ylim(0, 1)

@register("ecdf")
class ECDFLayer(CDFLayer):
    pass
