import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QGridLayout, QMessageBox, QPushButton
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from camera_thread import CameraThread
import base64
import mysql.connector
import numpy as np

class ReturnPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.user_id = None  # To store the recognized researcher ID

        # Main layout
        main_layout = QVBoxLayout(self)

        # Title Label
        self.title_label = QLabel('Return')
        self.title_label.setStyleSheet("font-family: 'Times [Adobe]'; color: #ffffff; padding: 15px; font-size: 20px; font-weight: bold;")

        # Widget content area
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Details layout using GridLayout
        self.details_layout = QGridLayout()

        # label 
        self.label = QLabel('')
        self.details_layout.addWidget(self.label)

        # Add the GridLayout to the main layout
        layout.addLayout(self.details_layout)

        widget.setLayout(layout)
        widget.setStyleSheet("QWidget {background-color: #303030; border-radius: 10px; color: #ffffff; font-size: 15px;}")

        # Add widgets to layout
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def loadreturnpage(self):
        self.label.setText("Name:"+(self.user_id))
        self.user_id = id

    def clear_fields(self):
        self.rname.setText("Waiting for face scan...")



        