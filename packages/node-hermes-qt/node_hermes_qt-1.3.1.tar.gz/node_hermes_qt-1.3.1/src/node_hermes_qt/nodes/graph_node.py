import time
from typing import Dict, Literal

import pyqtgraph as pg
from node_hermes_core.depencency.node_dependency import NodeDependency
from node_hermes_core.nodes.generic_node import GenericNode
from pydantic import BaseModel
from qtpy import QtCore, QtWidgets

from .data_tracker_node import DataTrackerNode, DataTrackerPoint
from .generic_qt_node import GenericNodeWidget, GenericQtNode
from .plot_common import PlotLineConfig, PlotMarkerConfig

# Set background color
pg.setConfigOption("background", "w")


class PlotTraceConfig(BaseModel):
    line: PlotLineConfig = PlotLineConfig()
    marker: PlotMarkerConfig = PlotMarkerConfig()


class TimeseriesTrace:
    datapoint: DataTrackerPoint
    plot_widget: pg.PlotWidget
    plot_trace: pg.PlotDataItem

    def __init__(
        self,
        trace_name: str,
        config: PlotTraceConfig,
        plot_widget: pg.PlotWidget,
        datapoint: DataTrackerPoint,
        trace_id: int,
    ):
        self.config = config
        self.trace_name = trace_name
        self.plot_widget = plot_widget
        self.datapoint = datapoint
        self.start_time = time.time()
        self.plot_trace = self.plot_widget.plot(name=self.trace_name)
        self.plot_trace.setPen(self.config.line.get_pen(trace_id))

        # enable marker
        if config.marker:
            self.plot_trace.setSymbol(config.marker.symbol)
            self.plot_trace.setSymbolBrush(config.marker.get_brush(trace_id))
            self.plot_trace.setSymbolSize(config.marker.size)
            self.plot_trace.setSymbolPen(config.marker.get_pen(trace_id))

    def update_data(self):
        """Updates the data in the plot"""
        timestamps, series = self.datapoint.get_values()
        self.plot_trace.setData(timestamps - self.start_time, series)  # type: ignore


class TimeseriesPlotWidget(GenericNodeWidget):
    class Config(BaseModel):
        traces: Dict[str, "TimeseriesPlotNode.GraphTraceConfig"]

    active_series: Dict[DataTrackerPoint, TimeseriesTrace]
    node: "TimeseriesPlotNode"

    def __init__(self, node: "TimeseriesPlotNode"):
        super().__init__(node)
        self.active_series = {}

        self.plotter = pg.PlotWidget()

        self.plotter.addLegend()
        self.plotter.showGrid(x=True, y=True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.plotter)

        self.setLayout(layout)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(100)

    def add_datapoint(self, trace_name: str, config: PlotTraceConfig, data: DataTrackerPoint):
        if data in self.active_series:
            return

        self.active_series[data] = TimeseriesTrace(trace_name, config, self.plotter, data, len(self.active_series))

    def update_data(self):
        """Regenerates the trace for all the active series"""

        for trace_name, trace in self.node.config.traces.items():
            self.add_datapoint(trace_name, trace, self.node.tracker_node.get_timeseries_trace(trace.source))

        for series in self.active_series.values():
            series.update_data()


class TimeseriesPlotNode(GenericNode, GenericQtNode):
    class GraphTraceConfig(PlotTraceConfig):
        source: str

    class Config(GenericNode.Config, GenericQtNode.Config, TimeseriesPlotWidget.Config):
        type: Literal["graph"] = "graph"
        tracker: str | DataTrackerNode.Config

        # @classmethod
        # def default(cls):
        #     return cls()

    config: Config

    def __init__(self, config: Config):
        # if config is None:
        # config = self.Config.default()
        super().__init__(config=config)

        self.base_dependency = NodeDependency(name="tracker_node", config=config.tracker, reference=DataTrackerNode)
        self.dependency_manager.add(self.base_dependency)

    def init(self, tracker_node: DataTrackerNode):  # type: ignore
        super().init()
        self.tracker_node = tracker_node

    @property
    def widget(self):
        """Get the widget class for this component"""
        return TimeseriesPlotWidget

    def deinit(self):
        super().deinit()
