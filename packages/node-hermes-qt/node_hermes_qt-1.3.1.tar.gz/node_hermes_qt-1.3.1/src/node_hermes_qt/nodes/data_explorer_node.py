from enum import Enum
from typing import Dict, List, Literal

# from node_hermes_core import MultiPointDataPacket, SinglePointDataPacket
# from node_hermes_core.nodes import ThreadedSinkNode
from node_hermes_core.depencency.node_dependency import NodeDependency
from node_hermes_core.nodes.generic_node import GenericNode
from pydantic import BaseModel, Field
from qtpy import QtCore, QtGui, QtWidgets

from node_hermes_qt.nodes.data_tracker_node import DataTrackerNode
from node_hermes_qt.nodes.graph_node import TimeseriesPlotNode

from .data_tracker_node import DataTrackerNode, DataTrackerPoint
from .generic_qt_node import GenericNodeWidget, GenericQtNode

# from .datapoint import DataTrackerPoint
# from .displays.display_widget import NumberGraphDisplay
# from .graph_widget import TimeseriesGraphDisplay


class GraphInfoField(Enum):
    NAME = "Name"
    LAST_VALUE = "Last Value"
    FREQUENCY = "Frequency"
    COUNT = "Point Count"
    AGE = "Age"
    POINTS = "Points"


class QColumnSelector(QtWidgets.QMenu):
    """Column selector menu"""

    change_signal = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.checkable_actions: Dict[GraphInfoField, QtGui.QAction] = {}
        # Add the checkable actions
        for column in GraphInfoField:
            action = self.addAction(column.value)
            action.setCheckable(True)
            action.setChecked(False)
            action.triggered.connect(self.change_signal.emit)
            self.checkable_actions[column] = action

    def set_selected_columns(self, columns: List[GraphInfoField]):
        """Set the selected columns

        Args:
            columns (List[AudiogramModel.AudiogramInfoField]): The columns to select
        """

        for column, action in self.checkable_actions.items():
            action.setChecked(column in columns)
        self.change_signal.emit()

    def get_selected_columns(self) -> List[GraphInfoField]:
        """Get the selected columns

        Returns:
            List[AudiogramModel.AudiogramInfoField]: The selected columns
        """
        return [column for column, action in self.checkable_actions.items() if action.isChecked()]


class SeriesPlotVisualisationDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, column: GraphInfoField, component: "DataExplorerNode"):
        super().__init__()
        self.component = component
        self.column = column

    def displayText(self, data, locale: QtCore.QLocale) -> str:  # type: ignore
        series: DataTrackerPoint | str | None = data

        if isinstance(series, str) or series is None:
            return str(series)

        if self.column == GraphInfoField.NAME:
            return series.name

        elif self.column == GraphInfoField.LAST_VALUE:
            if isinstance(series.last_value, float):
                return f"{series.last_value:.2f}"
            else:
                return str(series.last_value)

        elif self.column == GraphInfoField.FREQUENCY:
            return f"{series.frequency_counter.frequency:.2f}Hz"

        elif self.column == GraphInfoField.COUNT:
            return str(series.frequency_counter.count)

        elif self.column == GraphInfoField.AGE:
            return f"{series.frequency_counter.last_packet_age:.2f}s"

        elif self.column == GraphInfoField.POINTS:
            if series.timestamps is None:
                return "0"

            return f"{len(series.timestamps)}"

        else:
            return super().displayText(data, locale)

    def paint(self, painter, option, index):
        series: DataTrackerPoint | str | None = index.data()

        if isinstance(series, str) or series is None:
            return super().paint(painter, option, index)

        # Set color based on age
        age = series.frequency_counter.last_packet_age
        config = self.component.config.fade_config

        if age > config.fade_end_age:
            darkness = config.max_fade_darkness
        elif age > config.fade_start_age:
            darkness = int(
                config.max_fade_darkness * (age - config.fade_start_age) / (config.fade_end_age - config.fade_start_age)
            )
        else:
            darkness = 0

        if darkness > 0:
            color = QtGui.QColor(255 - darkness, 255 - darkness, 255 - darkness)
            painter.fillRect(option.rect, color)  # type: ignore

        return super().paint(painter, option, index)


class SeriesPlotTreeItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, series: DataTrackerPoint):
        super().__init__()
        self.series = series
        for i in range(10):
            self.setData(i, QtCore.Qt.ItemDataRole.DisplayRole, self.series)


class SeriesPlotGroupItem(QtWidgets.QTreeWidgetItem):
    item: QtWidgets.QTreeWidgetItem  # The group tree item, of this group
    name: str  # The name of the group
    child_groups: Dict[str, "SeriesPlotGroupItem"]
    child_items: Dict[str, SeriesPlotTreeItem]

    def __init__(self, name: str = "", parent_item: QtWidgets.QTreeWidgetItem | None = None):
        super().__init__()
        self.name = name
        if parent_item:
            self.item = parent_item
        else:
            self.item = self

        # Set name of the group
        self.setText(0, self.name)

        # Set the subgroups
        self.child_groups = {}
        self.child_items = {}

    def insert_child(self, name: str, item: SeriesPlotTreeItem):
        name_sections = name.split(".")
        base_name, remaining_sections = name_sections[0], ".".join(name_sections[1:])

        # If there is only one section, add the series to the current group
        if len(name_sections) == 1:
            item.series.display_name = name

            self.child_items[name] = item
            self.item.addChild(item)
            self.item.setExpanded(True)
            
            return item

        else:
            # If the value does to exist, create a new group
            if base_name not in self.child_groups:
                group = SeriesPlotGroupItem(base_name)
                self.item.addChild(group)
                self.child_groups[base_name] = group

                self.item.setExpanded(True)
            # Recursively insert the subgroup
            return self.child_groups[base_name].insert_child(remaining_sections, item)

    def remove_child(self, name: str, item: SeriesPlotTreeItem):
        """Remove the child with the given name and value"""
        print(f"Removing child: {name}")
        name_sections = name.split(".")
        base_name, remaining_sections = name_sections[0], ".".join(name_sections[1:])

        if len(name_sections) == 1:
            if name in self.child_items:
                self.child_items.pop(name)
                self.item.removeChild(item)
        else:
            if base_name in self.child_groups:
                self.child_groups[base_name].remove_child(remaining_sections, item)
                if len(self.child_groups[base_name].child_items) == 0:
                    self.item.removeChild(self.child_groups[base_name])
                    self.child_groups.pop(base_name)


class QPlotWidget(QtWidgets.QWidget):
    def __init__(self, component: "DataExplorerNode", items_to_plot: List[DataTrackerPoint], parent=None):
        print(f"Creating plot widget with items: {items_to_plot}")


class DataExplorerWidget(GenericNodeWidget):
    root_item: SeriesPlotGroupItem
    data_viewer_items: Dict[DataTrackerPoint, SeriesPlotTreeItem]
    node: "DataExplorerNode"
    graph_widgets = []

    class Config(BaseModel):
        class StalenessIndicatorConfig(BaseModel):
            fade_start_age: float = Field(description="The age at which the fader will start fading", default=1)
            fade_end_age: float = Field(description="The age at which the fader will be fully faded", default=10)
            max_fade_darkness: int = Field(description="The maximum darkness of the fader", default=100)

        filter_regex: str | None = Field(description="Filter regex to filter the data points", default=None)

        fade_config: StalenessIndicatorConfig = Field(
            description="Fade configuration", default_factory=StalenessIndicatorConfig
        )
        columns: List[GraphInfoField] = Field(
            description="The columns to display",
            default_factory=lambda: [GraphInfoField.NAME, GraphInfoField.LAST_VALUE, GraphInfoField.FREQUENCY],
        )

    def __init__(self, component: "DataExplorerNode"):
        super().__init__(component)
        self.data_viewer_items = {}

        top_bar_layout = QtWidgets.QHBoxLayout()
        self.column_selector_toolbutton = QtWidgets.QToolButton()
        self.column_selector_toolbutton.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self.column_selector_toolbutton.setText("Columns")
        self.column_selector_menu = QColumnSelector()
        self.column_selector_toolbutton.setMenu(self.column_selector_menu)
        self.column_selector_menu.set_selected_columns(component.config.columns)
        self.column_selector_menu.change_signal.connect(self.update_columns)
        self.column_selector_toolbutton.clicked.connect(self.column_selector_toolbutton.showMenu)

        self.clear_button = QtWidgets.QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_columns)

        self.create_graph_button = QtWidgets.QPushButton("Create Graph")
        self.create_graph_button.clicked.connect(self.create_graph)

        top_bar_layout.addStretch()
        top_bar_layout.addWidget(self.create_graph_button)
        top_bar_layout.addWidget(self.clear_button)
        top_bar_layout.addWidget(self.column_selector_toolbutton)

        # Create the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(top_bar_layout)
        self.treeWidget = QtWidgets.QTreeWidget()
        layout.addWidget(self.treeWidget)
        self.setLayout(layout)

        self.root_item = SeriesPlotGroupItem(parent_item=self.treeWidget.invisibleRootItem())
        self.treeWidget.setIndentation(10)

        # Set size of first columm to 200
        self.treeWidget.setColumnWidth(0, 250)
        
        # Allos multiple selection
        self.treeWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)

        # Set up timer to update the widget
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(250)

        self.update_columns()

    def create_graph(self):
        selected_items = self.selected_items

        if len(selected_items) == 0:
            return

        # Create new node
        node = TimeseriesPlotNode(
            config=TimeseriesPlotNode.Config(
                tracker="none",
                traces={item.id: TimeseriesPlotNode.GraphTraceConfig(source=item.id) for item in selected_items},
            )
        )
        node.init(self.node.tracker_node)
        widget = node.widget(node)
        widget.show()
        self.graph_widgets.append(widget)

    @property
    def selected_items(self) -> list[DataTrackerPoint]:
        # Return the selected items
        selected_items = self.treeWidget.selectedItems()
        return [item.series for item in selected_items if isinstance(item, SeriesPlotTreeItem)]

    def clear_columns(self):
        for item in self.selected_items:
            item.clear()

    def update_columns(self):
        self.node.config.columns = self.column_selector_menu.get_selected_columns()
        self.set_column_names(self.node.config.columns)

    def set_column_names(self, columns: List[GraphInfoField]):
        print(f"Setting columns: {columns}")
        self.treeWidget.setColumnCount(len(columns))
        self.treeWidget.setHeaderLabels([column.value for column in columns])

        self.delegates = []
        for i in range(len(columns)):
            delegate = SeriesPlotVisualisationDelegate(columns[i], self.node)
            self.delegates.append(delegate)
            self.treeWidget.setItemDelegateForColumn(i, delegate)

    def update_data(self):
        """Update the widget"""

        # Remove the data viewer items which are not in the data viewer items
        for point, item in list(self.data_viewer_items.items()):
            if point not in self.node.tracker_node.tracked_points.values():
                self.root_item.remove_child(point.id, item)
                self.data_viewer_items.pop(point)

        # Check if the widget is still active
        if not self.node.is_active():
            self.treeWidget.setStyleSheet("background-color: lightgray")

        else:
            self.treeWidget.setStyleSheet("")

            # Update the data viewer items which are not in the data viewer items
            for name, point in self.node.tracker_node.tracked_points.items():
                if point not in self.data_viewer_items:
                    series = SeriesPlotTreeItem(point)
                    self.root_item.insert_child(point.id, series)
                    self.data_viewer_items[point] = series

            self.treeWidget.viewport().update()


class DataExplorerNode(GenericNode, GenericQtNode):
    class Config(GenericNode.Config, GenericQtNode.Config, DataExplorerWidget.Config):
        type: Literal["data_explorer"] = "data_explorer"
        tracker: str | DataTrackerNode.Config

    config: Config

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
        return DataExplorerWidget

    def deinit(self):
        super().deinit()
