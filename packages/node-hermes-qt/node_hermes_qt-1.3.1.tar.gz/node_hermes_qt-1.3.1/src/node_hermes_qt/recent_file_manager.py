import os
from datetime import datetime

# from fbs_runtime.excepthook.sentry import SentryExceptionHandler
from pydantic import BaseModel, Field
from qtpy import QtCore, QtWidgets


class RecentFileLabel(QtWidgets.QLabel):
    on_load = QtCore.Signal(str)
    on_edit = QtCore.Signal(str)
    on_remove = QtCore.Signal(str)

    def __init__(self, config_path: str):
        super().__init__(config_path)
        self.config_path = config_path

        # Set text to be a link
        self.setText(f'<a href="{config_path}">{config_path}</a>')

        # Make hperlink black
        self.setStyleSheet("color: black;")

        # On click load the config
        self.linkActivated.connect(self.on_load)

        # Allow right mouse click to edit
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)

    def context_menu(self, pos: QtCore.QPoint):
        menu = QtWidgets.QMenu()
        edit_action = menu.addAction("Edit")
        remove_action = menu.addAction("Remove")
        load_action = menu.addAction("Load")

        action = menu.exec_(self.mapToGlobal(pos))

        if action == edit_action:
            self.on_edit.emit(self.config_path)
        elif action == remove_action:
            self.on_remove.emit(self.config_path)

        elif action == load_action:
            self.on_load.emit(self.config_path)


class RecentFileManager(QtWidgets.QWidget):
    on_load = QtCore.Signal(str)
    on_edit = QtCore.Signal(str)

    class RecentFile(BaseModel):
        path: str
        accessed: datetime = Field(default_factory=datetime.now)

    class State(BaseModel):
        recent_files: "dict[str,RecentFileManager.RecentFile]" = Field(default_factory=dict)

        def add(self, path: str):
            self.recent_files[path] = RecentFileManager.RecentFile(path=path)

        def remove(self, path: str):
            if path in self.recent_files:
                del self.recent_files[path]

        def get_recent_files(self, ascending: bool = False):
            return sorted(self.recent_files.values(), key=lambda x: x.accessed, reverse=ascending)

        def get_last_loaded_config(self):
            if len(self.recent_files) > 0:
                return list(self.recent_files.keys())[0]
            return

        @property
        def last_browse_directory(self):
            if len(self.recent_files) > 0:
                return os.path.dirname(list(self.recent_files.keys())[0])
            return os.getcwd()

    def __init__(self, state: State):
        super().__init__()
        self.state = state

        self.recent_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.recent_layout)

        self.rebuild()

    def rebuild(self):
        # Remove all widgets
        for i in reversed(range(self.recent_layout.count())):
            self.recent_layout.itemAt(i).widget().deleteLater()

        for file in self.state.get_recent_files():
            label = RecentFileLabel(file.path)
            self.recent_layout.addWidget(label)
            label.on_load.connect(self.on_load)
            label.on_edit.connect(self.on_edit)
            label.on_remove.connect(self.remove)

    def add(self, path: str):
        self.state.add(path)
        self.rebuild()

    def remove(self, path: str):
        self.state.remove(path)
        self.rebuild()
