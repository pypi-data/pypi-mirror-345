import logging
from typing import List, Literal

from node_hermes_core.depencency.node_dependency import RootNodeDependency
from node_hermes_core.nodes.generic_node import GenericNode
from node_hermes_core.nodes.root_nodes import RootNode
from qt_custom_treewidget import ColumnNames, TreeItem, TreeviewViewer
from qtpy import QtCore, QtGui, QtWidgets

from node_hermes_qt.nodes.generic_qt_node import GenericNodeWidget, GenericQtNode

from ..ui.toolbar import Ui_Form


class ToolbarWidget(QtWidgets.QWidget, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)


class NodeInfoFields(ColumnNames):
    NAME = "Name"
    TYPE = "Type"
    STATUS = "Status"
    INFO = "Info"
    QUEUE = "Queue"


class NodeTreeItem(TreeItem):
    def __init__(self, node: GenericNode, root_item: QtWidgets.QTreeWidgetItem | None = None):
        super().__init__()
        self.treeitem = root_item if root_item else self
        self.set_node(node)

    def set_node(self, node: GenericNode):
        self.node = node
        self.treeitem.setExpanded(True)
        for name, node in self.node.managed_child_nodes.items():
            self.treeitem.addChild(NodeTreeItem(node))

    def get_text(self, column_type: ColumnNames):
        if column_type == NodeInfoFields.NAME:
            return self.node.name
        elif column_type == NodeInfoFields.STATUS:
            return self.node.state.name
        elif column_type == NodeInfoFields.TYPE:
            return self.node.__class__.__name__
        elif column_type == NodeInfoFields.INFO:
            return self.node.info_string
        elif column_type == NodeInfoFields.QUEUE:
            return self.node.queue_string
        return "Unknown"

    def get_color(self):
        if self.node.state == GenericNode.State.ACTIVE:
            return QtGui.QColor("lightgreen")
        elif self.node.state == GenericNode.State.INITIALIZING:
            return QtGui.QColor("yellow")
        elif self.node.state == GenericNode.State.ERROR:
            return QtGui.QColor("lightcoral")
        elif self.node.state == GenericNode.State.STOPPED:
            return QtGui.QColor("lightyellow")

        return None

    def expand_recursive(self):
        self.treeitem.setExpanded(True)
        for i in range(self.treeitem.childCount()):
            child = self.treeitem.child(i)
            if isinstance(child, NodeTreeItem):
                child.expand_recursive()


class NodeManagerWidget(GenericNodeWidget):
    root_item: NodeTreeItem | None = None
    node: "NodeManagerNode"

    def __init__(self, node: "NodeManagerNode"):
        super().__init__(node)

        self.devices = {}
        self.treeitems = {}

        self.toolbar = ToolbarWidget()
        self.toolbar.start_btn.clicked.connect(self.start_selected_device)
        self.toolbar.stop_btn.clicked.connect(self.stop_selected_device)

        self.viewer_widget = TreeviewViewer()

        # self.viewer_widget.itemSelectionChanged.connect(self.on_selection_change)
        self.log = logging.getLogger(__name__)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.viewer_widget)

        self.setLayout(layout)
        self.viewer_widget.set_columns([t for t in NodeInfoFields])

        # Allow multiple selection
        self.viewer_widget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)

        # Use a qt timer to update the ui
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(500)

    def update_ui(self):
        if self.node.root_node is None:
            self.root_item = None
            self.viewer_widget.clear()

        elif self.root_item is not None:
            self.viewer_widget.refresh_ui()

        else:
            self.root_item = NodeTreeItem(self.node.root_node, self.viewer_widget.invisibleRootItem())

            # Expand all clildren
            self.root_item.expand_recursive()

    @property
    def selected_nodes(self) -> List[GenericNode]:
        selected_items = self.viewer_widget.get_selected_items()
        return [item.node for item in selected_items if isinstance(item, NodeTreeItem)]

    def start_selected_device(self):
        for node in self.selected_nodes:
            node.attempt_init()

    def stop_selected_device(self):
        for node in self.selected_nodes:
            node.attempt_deinit()

    def set_columns(self, collumns: List[ColumnNames]):
        self.viewer_widget.set_columns(collumns)


class NodeManagerNode(GenericNode, GenericQtNode):
    class Config(GenericNode.Config, GenericQtNode.Config):
        type: Literal["node_manager"] = "node_manager"

    config: Config
    root_node: RootNode | None = None

    def __init__(self, config: Config):
        super().__init__(config=config)

        self.root_node_depenceny = RootNodeDependency(name="root_node")
        self.dependency_manager.add(self.root_node_depenceny)

    def init(self, root_node: RootNode):  # type: ignore
        super().init()
        self.root_node = root_node

    @property
    def widget(self):
        """Get the widget class for this component"""
        return NodeManagerWidget

    def deinit(self):
        self.root_node = None
        super().deinit()
