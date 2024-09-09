from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLineEdit, QGridLayout
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QPainter, QIntValidator
import qtawesome as qta


class AddEquipmentPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        # Main layout
        main_layout = QVBoxLayout(self)

        # Title Label
        self.title_label = QLabel('Add Equipment')
        self.title_label.setStyleSheet("""
            font-family: "Times [Adobe]";
            color: #ffffff;
            padding: 15px;
            font-size: 20px;
            font-weight: bold;
        """)

        # Widget content area
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Details layout using GridLayout
        details_layout = QGridLayout()

        # Equipment image
        pixmap = QPixmap(self.get_default_image())  # Use default image
        self.equipment_image = QLabel()
        self.equipment_image.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))  # Scale image
        self.equipment_image.setFixedSize(300, 300)
        self.equipment_image.setStyleSheet("""border:1px solid #ffffff""")
        self.equipment_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add Image Button
        image_button = QPushButton(qta.icon('ri.image-add-fill', color='black'), "")
        image_button.setIconSize(QSize(24, 24))
        image_button.setFixedSize(30, 30)
        image_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border-radius: 15px;
                color: #000000;
            }
            QPushButton:hover {
                background-color: #383838;
            }
        """)
        image_button.clicked.connect(self.select_image)

        # Stack the image and button
        image_layout = QVBoxLayout(self.equipment_image)
        image_layout.addWidget(image_button, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        # Add image to GridLayout in row 0, column 0 (spanning rows)
        details_layout.addWidget(self.equipment_image, 0, 0, 3, 1, Qt.AlignmentFlag.AlignLeft)

        # Labels for Name, ID, Total (placed in row 0, column 1; row 1, column 1; row 2, column 1 respectively)
        name_label = QLabel("Name:")
        id_label = QLabel("Equipment ID:")
        total_label = QLabel("Total:")

        details_layout.addWidget(name_label, 0, 1, Qt.AlignmentFlag.AlignVCenter)
        details_layout.addWidget(id_label, 1, 1, Qt.AlignmentFlag.AlignVCenter)
        details_layout.addWidget(total_label, 2, 1, Qt.AlignmentFlag.AlignVCenter)

        # Input fields for Name, ID, and Total (placed in row 0, column 2; row 1, column 2; row 2, column 2 respectively)
        # Name Input
        self.a_ename = QLineEdit()
        self.a_ename.setStyleSheet("background-color: #ffffff; color: #000000;")
        details_layout.addWidget(self.a_ename, 0, 2, Qt.AlignmentFlag.AlignVCenter)

        # ID Display
        self.a_eid = QLabel("E1001")
        self.a_eid.setStyleSheet("color: #ffffff;")
        details_layout.addWidget(self.a_eid, 1, 2, Qt.AlignmentFlag.AlignVCenter)

        # Number Picker for Total (in row 2, column 2)
        num_layout = QHBoxLayout()
        self.a_etotal = QLineEdit("0")
        self.a_etotal.setValidator(QIntValidator())
        self.a_etotal.setFixedSize(50, 30)
        self.a_etotal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.a_etotal.setStyleSheet("background-color: #ffffff; color: #000000; border-radius: 5px;")

        minus_button = QPushButton("-")
        minus_button.setFixedSize(30, 30)
        minus_button.clicked.connect(self.decrease_total)
        plus_button = QPushButton("+")
        plus_button.setFixedSize(30, 30)
        plus_button.clicked.connect(self.increase_total)

        minus_button.setStyleSheet("background-color: #ffffff; border-radius: 15px; color:#000000;")
        plus_button.setStyleSheet("background-color: #ffffff; border-radius: 15px; color:#000000;")

        num_layout.addWidget(minus_button)
        num_layout.addWidget(self.a_etotal)
        num_layout.addWidget(plus_button)

        # Add the number picker to GridLayout
        details_layout.addLayout(num_layout, 2, 2, Qt.AlignmentFlag.AlignVCenter)

        # Add the GridLayout to the main layout
        layout.addLayout(details_layout)

        # Add button section layout
        button_section = QHBoxLayout()
        button_section.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Add Save button
        self.a_esave = QPushButton("Add")
        self.a_esave.setStyleSheet("font-size: 15px; color: #000000; background-color: #ffffff; border-radius: 10px;")
        self.a_esave.setFixedSize(80, 25)
        self.a_esave.clicked.connect(lambda: self.add())
        button_section.addWidget(self.a_esave)

        layout.addLayout(button_section)
        widget.setLayout(layout)
        widget.setStyleSheet("""
            QWidget {
                background-color: #303030;
                border-radius: 10px;
                color: #ffffff;
                font-size: 15px;
            }
        """)

        # Add widgets to layout
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def set_rounded_pixmap(self, label, pixmap):
        rounded_pixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        mask = QPixmap(rounded_pixmap.size())
        mask.fill(Qt.transparent)
        painter = QPainter(mask)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.black)
        painter.drawRoundedRect(mask.rect(), 15, 15)
        rounded_pixmap.setMask(mask.mask())
        painter.end()
        label.setPixmap(rounded_pixmap)

    def decrease_total(self):
        current_value = int(self.a_etotal.text())
        if current_value > 0:
            self.a_etotal.setText(str(current_value - 1))

    def increase_total(self):
        current_value = int(self.a_etotal.text())
        self.a_etotal.setText(str(current_value + 1))

    def select_image(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.xpm *.jpg)")
        if file_path:
            pixmap = QPixmap(file_path)
            self.set_rounded_pixmap(self.equipment_image, pixmap)

    def add(self):
        self.main_window.show_equipment()
        print("Add function")

    def get_default_image(self):
        # Create a default image using a Qt Awesome icon
        icon = qta.icon('fa.file-image-o', color='white')
        pixmap = QPixmap(180, 180)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        icon.paint(painter, pixmap.rect())
        painter.end()
        return pixmap
