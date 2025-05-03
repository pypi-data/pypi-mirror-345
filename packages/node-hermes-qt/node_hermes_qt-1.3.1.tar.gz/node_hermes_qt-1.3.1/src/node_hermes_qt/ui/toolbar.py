# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'toolbar.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
)
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QSizePolicy, QSpacerItem


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(676, 90)
        self.horizontalLayout = QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.start_btn = QPushButton(Form)
        self.start_btn.setObjectName("start_btn")

        self.horizontalLayout.addWidget(self.start_btn)

        self.stop_btn = QPushButton(Form)
        self.stop_btn.setObjectName("stop_btn")

        self.horizontalLayout.addWidget(self.stop_btn)

        self.horizontalSpacer = QSpacerItem(493, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Form", None))
        self.start_btn.setText(QCoreApplication.translate("Form", "Start", None))
        self.stop_btn.setText(QCoreApplication.translate("Form", "Stop", None))

    # retranslateUi
