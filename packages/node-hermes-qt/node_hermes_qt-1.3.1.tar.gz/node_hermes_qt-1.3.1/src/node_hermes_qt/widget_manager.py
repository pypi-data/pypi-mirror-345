from typing import List, Tuple

# from fbs_runtime.excepthook.sentry import SentryExceptionHandler
from node_hermes_core.nodes.root_nodes import RootNode
from qtpy import QtWidgets, QtCore, QtGui

from node_hermes_qt.nodes.generic_qt_node import GenericQtNode, WindowConfig


class WidgetManager(QtWidgets.QWidget):
    root_node: RootNode | None = None
    spawned_widgets: List[Tuple[QtWidgets.QWidget|None, QtWidgets.QWidget]] = []

    def __init__(self, mainwindow: QtWidgets.QMainWindow):
        super().__init__()
        self.spawned_widgets = []
        self.mainwindow = mainwindow

        # Create tab widget
        self.tabWidget = QtWidgets.QTabWidget()

        # add tab widget to main window
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.tabWidget)
        self.setLayout(layout)

    def attach(self, root_node: RootNode):
        self.root_node = root_node

        # Initalize the widgets
        for node in root_node.get_flat_node_list():
            if isinstance(node, GenericQtNode):
                assert isinstance(node.config, GenericQtNode.Config)
                if not node.config.interface:
                    continue

                widget = node.widget(node)

                if node.config.interface.type == "tab":
                    self.tabWidget.addTab(widget, node.config.interface.name)
                    self.spawned_widgets.append((self.tabWidget, widget))

                elif node.config.interface.type == "dock":
                    dockwidget = QtWidgets.QDockWidget(node.config.interface.name)
                    dockwidget.setWidget(widget)
                    position = node.config.interface.position.to_qt()
                    
                    if node.config.interface.min_width is not None:
                        dockwidget.setMinimumWidth(node.config.interface.min_width)
                    
                    if node.config.interface.min_height is not None:
                        dockwidget.setMinimumHeight(node.config.interface.min_height)
                        
                    if position is not None:
                        self.mainwindow.addDockWidget(position, dockwidget)
                    else:
                        dockwidget.setFloating(True)
                        dockwidget.show()

                    self.spawned_widgets.append((dockwidget, widget))
                    
                elif isinstance(node.config.interface, WindowConfig):
                    widget.setWindowTitle(node.config.interface.name)
                    widget.show()

                    # If snap is defined snap to corner of the sceen with 50% width and height
                    total_monitor_width =  QtGui.QGuiApplication.primaryScreen().availableGeometry().width()
                    total_monitor_height =  QtGui.QGuiApplication.primaryScreen().availableGeometry().height()
                    
                    if node.config.interface.snap_position is not None:
                        # Set width and height to 50% of the screen
                        widget.resize(total_monitor_width // 2, total_monitor_height // 2)

                        if node.config.interface.snap_position == "top_left":
                            widget.move(0, 0)
                        elif node.config.interface.snap_position == "top_right":
                            widget.move(total_monitor_width // 2, 0)
                        elif node.config.interface.snap_position == "bottom_left":
                            widget.move(0, total_monitor_height // 2)
                        elif node.config.interface.snap_position == "bottom_right":
                            widget.move(total_monitor_width // 2, total_monitor_height // 2)
                            
        
                    self.spawned_widgets.append((None, widget))
                    
    def detach(self):
        for parent, widget in self.spawned_widgets:
            if parent is not None:
                if isinstance(parent, QtWidgets.QTabWidget):
                    parent.removeTab(parent.indexOf(widget))
                elif isinstance(parent, QtWidgets.QDockWidget):
                    parent.close()

            # If widget has a deinit method call it
            if hasattr(widget, "deinit"):
                widget.deinit() # type: ignore

            widget.close()

        self.spawned_widgets = []
        self.root_node = None
