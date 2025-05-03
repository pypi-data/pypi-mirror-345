import asyncio

from node_hermes_core.nodes import GenericNode, AsyncGenericNode

# from qt_utils import catch_exception
from qtpy import QtCore, QtWidgets


class QConnectionDisplayWidget(QtWidgets.QWidget):
    async_init_task: asyncio.Task | None = None
    async_deinit_task: asyncio.Task | None = None
    state_update_signal = QtCore.Signal()

    def __init__(self, component: GenericNode, inline: bool = True):
        super().__init__()
        self.component = component
        self.inline = inline

        if self.inline:
            layout = QtWidgets.QHBoxLayout()
            self.setLayout(layout)

            self.connection_state_line = QtWidgets.QLineEdit()
            self.connection_state_line.setReadOnly(True)
            layout.addWidget(self.connection_state_line)

            self.init_deinit_button = QtWidgets.QPushButton("Init")
            self.init_deinit_button.clicked.connect(self.toggle_connection)
            layout.addWidget(self.init_deinit_button)

        else:
            layout = QtWidgets.QVBoxLayout()
            self.setLayout(layout)

            self.connection_state_line = QtWidgets.QLineEdit()
            self.connection_state_line.setReadOnly(True)
            layout.addWidget(self.connection_state_line)

            self.init_deinit_button = QtWidgets.QPushButton("Init")
            self.init_deinit_button.clicked.connect(self.toggle_connection)
            layout.addWidget(self.init_deinit_button)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_connection_state)
        self.timer.start(2000)

        self.update_connection_state()

    def init_component(self):
        self.component.state = GenericNode.State.INITIALIZING
        self.component.attempt_init()
        self.update_connection_state()  
        
        if isinstance(self.component, AsyncGenericNode):
            asyncio.ensure_future(self.component.attempt_init(**self.component.collect_depependencies())) 
        elif isinstance(self.component, GenericNode):
            self.async_init_task = self.component.attempt_init(**self.component.collect_depependencies())
            self.async_init_task.add_done_callback(self.update_connection_state)
            
            loop = asyncio.get_event_loop()
            self.async_init_task = loop.create_task(
                self.component.attempt_init(**self.component.collect_depependencies())
            )

    def deinit_component(self, reason_error: bool = False):
        self.component.state = GenericNode.State.DEINITIALISING
        
        if isinstance(self.component, AsyncGenericNode):
            asyncio.ensure_future(self.component.attempt_deinit())
        elif isinstance(self.component, GenericNode):   
            self.async_deinit_task = self.component.attempt_deinit()
            self.async_deinit_task.add_done_callback(self.update_connection_state)
            
            loop = asyncio.get_event_loop()
            self.async_deinit_task = loop.create_task(self.component.attempt_deinit())
            
        
                
        
    def toggle_connection(self):
        if self.component.state == GenericNode.State.ACTIVE:
            self.deinit_component()
        elif self.component.state == GenericNode.State.INITIALIZING:
            if self.async_init_task:
                self.async_init_task.cancel()
        else:
            self.init_component()

        self.update_connection_state()

    def update_connection_state(self):
        self.connection_state_line.setText(str(self.component.state.name))
        if self.component.state == GenericNode.State.ACTIVE:
            self.init_deinit_button.setText("Deinit")
        elif self.component.state == GenericNode.State.INITIALIZING:
            self.init_deinit_button.setText("Cancel")
        else:
            self.init_deinit_button.setText("Init")

        if self.component.state == GenericNode.State.ACTIVE:
            self.connection_state_line.setStyleSheet("background-color: lightgreen")
        elif self.component.state == GenericNode.State.INITIALIZING:
            self.connection_state_line.setStyleSheet("background-color: lightblue")
        elif self.component.state == GenericNode.State.ERROR:
            self.connection_state_line.setStyleSheet("background-color: lightcoral")

        else:
            self.connection_state_line.setStyleSheet("background-color: lightgrey")
        self.state_update_signal.emit()
