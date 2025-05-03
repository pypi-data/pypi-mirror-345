import time
from typing import Dict, Literal

import numpy as np
import pyqtgraph as pg
from node_hermes_core.depencency.node_dependency import NodeDependency
from node_hermes_core.nodes.generic_node import GenericNode
from pydantic import BaseModel
from qtpy import QtCore, QtWidgets

from .data_tracker_node import DataTrackerNode, DataTrackerPoint
from .generic_qt_node import GenericNodeWidget, GenericQtNode
from .plot_common import PlotFillConfig, PlotLineConfig


class TimeseriesTrace:
    class Config(BaseModel):
        line: PlotLineConfig = PlotLineConfig()
        fill: PlotFillConfig = PlotFillConfig()
        bins: int = 30
        density: bool = True

    datapoint: DataTrackerPoint
    plot_widget: pg.PlotWidget
    plot_trace: pg.PlotDataItem

    def __init__(
        self,
        trace_name: str,
        config: Config,
        plot_widget: pg.PlotWidget,
        datapoint: DataTrackerPoint,
        trace_id: int,
    ):
        self.config = config
        self.trace_name = trace_name
        self.plot_widget = plot_widget
        self.datapoint = datapoint
        self.start_time = time.time()

        self.plot_trace = self.plot_widget.plot(
            stepMode="center", fillLevel=0, fillOutline=True, brush=(0, 0, 255, 150), name=self.trace_name
        )

        self.plot_trace.setPen(self.config.line.get_pen(trace_id))
        self.plot_trace.setBrush(self.config.fill.get_brush(trace_id))

    def update_data(self):
        """Updates the data in the plot"""
        timestamps, series = self.datapoint.get_values()
        if len(series) == 0:
            self.plot_trace.setData([], [])
            return

        y, x = np.histogram(series, bins=self.config.bins, density=self.config.density)
        self.plot_trace.setData(x, y)


class HistogramWidget(GenericNodeWidget):
    class Config(BaseModel):
        traces: Dict[str, "HistogramNode.GraphTraceConfig"]

    active_series: Dict[DataTrackerPoint, TimeseriesTrace]
    node: "HistogramNode"

    def __init__(self, node: "HistogramNode"):
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

    def add_datapoint(self, trace_name: str, config: TimeseriesTrace.Config, data: DataTrackerPoint):
        if data in self.active_series:
            return

        self.active_series[data] = TimeseriesTrace(trace_name, config, self.plotter, data, len(self.active_series))

    def update_data(self):
        """Regenerates the trace for all the active series"""
        if not self.node.tracker_node:
            if self.node.state == GenericNode.State.STOPPED:
                # Stop the timer if the node is stopped
                self.timer.stop()

            return

        for trace_name, trace in self.node.config.traces.items():
            self.add_datapoint(trace_name, trace, self.node.tracker_node.get_timeseries_trace(trace.source))

        for series in self.active_series.values():
            series.update_data()


class HistogramNode(GenericNode, GenericQtNode):
    class GraphTraceConfig(TimeseriesTrace.Config):
        source: str

    class Config(GenericNode.Config, GenericQtNode.Config, HistogramWidget.Config):
        type: Literal["histogram"] = "histogram"
        tracker: str | DataTrackerNode.Config

    config: Config
    tracker_node: DataTrackerNode | None = None

    def __init__(self, config: Config):
        super().__init__(config=config)

        self.base_dependency = NodeDependency(name="tracker_node", config=config.tracker, reference=DataTrackerNode)
        self.dependency_manager.add(self.base_dependency)

    def init(self, tracker_node: DataTrackerNode):  # type: ignore
        super().init()
        self.tracker_node = tracker_node

    @property
    def widget(self):
        """Get the widget class for this component"""
        return HistogramWidget

    def deinit(self):
        self.tracker_node = None
        super().deinit()
