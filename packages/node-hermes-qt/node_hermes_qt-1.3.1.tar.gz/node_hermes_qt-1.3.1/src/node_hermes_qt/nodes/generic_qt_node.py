from abc import ABC, abstractmethod
from enum import Enum
from typing import Literal, Type

from pydantic import BaseModel,Field
from qtpy import QtCore, QtWidgets


class GenericNodeWidget(QtWidgets.QWidget):
    def __init__(self, node: "GenericQtNode"):
        super().__init__()
        self.node = node


class TabConfig(BaseModel):
    type: Literal["tab"]
    name: str


class DockConfig(BaseModel):
    class DockWidgetPosition(Enum):
        LEFT = "left"
        RIGHT = "right"
        TOP = "top"
        BOTTOM = "bottom"
        FLOATING = "floating"

        def to_qt(self) -> QtCore.Qt.DockWidgetArea | None:
            if self == DockConfig.DockWidgetPosition.LEFT:
                return QtCore.Qt.DockWidgetArea.LeftDockWidgetArea
            elif self == DockConfig.DockWidgetPosition.RIGHT:
                return QtCore.Qt.DockWidgetArea.RightDockWidgetArea
            elif self == DockConfig.DockWidgetPosition.TOP:
                return QtCore.Qt.DockWidgetArea.TopDockWidgetArea
            elif self == DockConfig.DockWidgetPosition.BOTTOM:
                return QtCore.Qt.DockWidgetArea.BottomDockWidgetArea
            elif self == DockConfig.DockWidgetPosition.FLOATING:
                return None

    type: Literal["dock"]
    name: str
    position: DockWidgetPosition
    min_width: int|None = None
    min_height: int|None = None
    
class WindowConfig(BaseModel):
    type: Literal["window"]
    name: str
    snap_position: Literal["top_left", "top_right", "bottom_left", "bottom_right"]|None = None
    
    
    
class GenericQtNode(ABC):
    class Config(BaseModel):
        interface: TabConfig | DockConfig | WindowConfig | None =  Field(discriminator='type')
        
    @property
    @abstractmethod
    def widget(self) -> Type[GenericNodeWidget]:
        raise NotImplementedError
    