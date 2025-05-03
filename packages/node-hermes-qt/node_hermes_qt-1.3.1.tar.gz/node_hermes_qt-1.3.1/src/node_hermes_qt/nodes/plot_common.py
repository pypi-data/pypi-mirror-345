from enum import Enum

import pyqtgraph as pg
from pydantic import BaseModel

PLOT_COLORS = [
    (230, 25, 75),
    (60, 180, 75),
    (255, 225, 25),
    (0, 130, 200),
    (245, 130, 48),
    (145, 30, 180),
    (70, 240, 240),
    (240, 50, 230),
    (210, 245, 60),
    (250, 190, 190),
    (0, 128, 128),
    (230, 190, 255),
    (170, 110, 40),
    (255, 250, 200),
    (0, 0, 0),
]


class PlotColor(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    YELLOW = "yellow"
    ORANGE = "orange"
    PURPLE = "purple"
    AUTO = "auto"

    def to_color(self) -> tuple[int, int, int]:
        if self == PlotColor.RED:
            return (255, 0, 0)
        elif self == PlotColor.GREEN:
            return (0, 255, 0)
        elif self == PlotColor.BLUE:
            return (0, 0, 255)
        elif self == PlotColor.YELLOW:
            return (255, 255, 0)
        elif self == PlotColor.ORANGE:
            return (255, 165, 0)
        elif self == PlotColor.PURPLE:
            return (128, 0, 128)
        else:
            return (0, 0, 0)

    @staticmethod
    def to_rgb(orig_color: "tuple[float, float, float] | PlotColor", trace_id: int) -> tuple[float, float, float]:
        if isinstance(orig_color, PlotColor):
            if orig_color == PlotColor.AUTO:
                return PLOT_COLORS[trace_id % len(PLOT_COLORS)]
            else:
                return orig_color.to_color()
        return orig_color


class PlotMarkerConfig(BaseModel):
    color: tuple[float, float, float] | PlotColor = PlotColor.AUTO
    size: int = 3
    symbol: str = "o"
    opacity: float = 255

    def get_brush(self, trace_id: int):
        return pg.mkBrush(color=PlotColor.to_rgb(self.color, trace_id) + (self.opacity,))

    def get_pen(self, trace_id: int):
        return pg.mkPen(None)


class PlotFillConfig(BaseModel):
    color: tuple[float, float, float] | PlotColor = PlotColor.AUTO
    opacity: float = 255 // 2

    def get_brush(self, trace_id: int):
        return pg.mkBrush(color=PlotColor.to_rgb(self.color, trace_id) + (self.opacity,))


class PlotLineConfig(BaseModel):
    color: tuple[float, float, float] | PlotColor = PlotColor.AUTO
    opacity: float = 255
    line_width: int = 2

    def get_pen(self, trace_id: int):
        if self.line_width == 0:
            return pg.mkPen(None)

        return pg.mkPen(color=PlotColor.to_rgb(self.color, trace_id) + (self.opacity,), width=self.line_width)
