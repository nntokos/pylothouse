from abc import ABC, abstractmethod
from .registry import register
from .utils import resolve_linestyle

class Layer(ABC):
    def __init__(self, spec):
        self.spec = spec

    @abstractmethod
    def draw(self, ax, df):
        ...

@register('line')
class LineLayer(Layer):
    def draw(self, ax, df):
        ax.plot(df[self.spec.x], df[self.spec.y],
                linestyle=resolve_linestyle(self.spec.style.style),
                linewidth=self.spec.style.width,
                marker=self.spec.style.marker,
                color=self.spec.style.color,
                label=self.spec.label_text)

@register('scatter')
class ScatterLayer(Layer):
    def draw(self, ax, df):
        ax.scatter(df[self.spec.x], df[self.spec.y],
                   marker=self.spec.style.marker or "o",
                   label=self.spec.label_text,
                   color=self.spec.style.color)

@register('hist')
class HistLayer(Layer):
    def draw(self, ax, df):
        ax.hist(df[self.spec.x],
                bins=self.spec.bins or 30,
                label=self.spec.label_text)