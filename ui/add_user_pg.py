from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLineEdit, QGridLayout, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QPainter
import qtawesome as qta
import re

class AddUserPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        # Main layout
        main_layout = QVBoxLayout(self)

        # Title Label
        self.title_label = QLabel('Add User')
        self.title_label.setStyleSheet("font-family: 'Times [Adobe]'; color: #ffffff; padding: 15px; font-size: 20px; font-weight: bold;")

        # Widget content area
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Details layout using GridLayout
        self.details_layout = QGridLayout()

        # Equipment image changed to user image
        pixmap = QPixmap(self.get_default_image())  # Use default image
        self.user_image = QLabel()
        self.user_image.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))  # Scale image
        self.user_image.setFixedSize(300, 300)
        self.user_image.setStyleSheet("border:1px solid #ffffff")
        self.user_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add Image Button
        image_button = QPushButton(qta.icon('ri.image-add-fill', color='black'), "")
        image_button.setIconSize(QSize(24, 24))
        image_button.setFixedSize(30, 30)
        image_button.setStyleSheet("QPushButton {background-color: #ffffff; border-radius: 15px; color: #000000;} QPushButton:hover {background-color: #383838;}")
        image_button.clicked.connect(self.select_image)

        # Stack the image and button
        image_layout = QVBoxLayout(self.user_image)
        image_layout.addWidget(image_button, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        # Add image to GridLayout in row 0, column 0 (spanning rows)
        self.details_layout.addWidget(self.user_image, 0, 0, 6, 1, Qt.AlignmentFlag.AlignLeft)

        # Category Selection
        category_label = QLabel("Category:")
        self.category_combo = QComboBox()
        self.category_combo.addItems(['Researcher', 'Lab Assistant'])
        self.category_combo.currentTextChanged.connect(self.update_ui)
        self.details_layout.addWidget(category_label, 0, 1, Qt.AlignmentFlag.AlignVCenter)
        self.details_layout.addWidget(self.category_combo, 0, 2, Qt.AlignmentFlag.AlignVCenter)

        # Name Input
        name_label = QLabel("Name:")
        self.a_uname = QLineEdit()
        self.a_uname.setStyleSheet("background-color: #ffffff; color: #000000;")
        self.details_layout.addWidget(name_label, 1, 1, Qt.AlignmentFlag.AlignVCenter)
        self.details_layout.addWidget(self.a_uname, 1, 2, Qt.AlignmentFlag.AlignVCenter)

        # User ID Display
        id_label = QLabel("User ID:")
        self.a_uid = QLabel("R0001")  # Default ID
        self.a_uid.setStyleSheet("color: #ffffff;")
        self.details_layout.addWidget(id_label, 2, 1, Qt.AlignmentFlag.AlignVCenter)
        self.details_layout.addWidget(self.a_uid, 2, 2, Qt.AlignmentFlag.AlignVCenter)

        # Phone Input
        phone_label = QLabel("Phone:")
        self.a_uphone = QLineEdit()
        self.a_uphone.setStyleSheet("background-color: #ffffff; color: #000000;")
        self.details_layout.addWidget(phone_label, 3, 1, Qt.AlignmentFlag.AlignVCenter)
        self.details_layout.addWidget(self.a_uphone, 3, 2, Qt.AlignmentFlag.AlignVCenter)

        # Email Input
        email_label = QLabel("Email:")
        self.a_uemail = QLineEdit()
        self.a_uemail.setStyleSheet("background-color: #ffffff; color: #000000;")
        self.details_layout.addWidget(email_label, 4, 1, Qt.AlignmentFlag.AlignVCenter)
        self.details_layout.addWidget(self.a_uemail, 4, 2, Qt.AlignmentFlag.AlignVCenter)

        # Password Input
        self.password_label = QLabel("Password:")
        self.a_upassword = QLineEdit()
        self.a_upassword.setEchoMode(QLineEdit.Password)
        self.a_upassword.setStyleSheet("background-color: #ffffff; color: #000000;")

        # Confirm Password Input
        self.confirm_password_label = QLabel("Confirm Password:")
        self.a_uconfirm_password = QLineEdit()
        self.a_uconfirm_password.setEchoMode(QLineEdit.Password)
        self.a_uconfirm_password.setStyleSheet("background-color: #ffffff; color: #000000;")

        # Dynamically added password fields based on category
        self.password_layout_index = self.details_layout.rowCount()  # Get current row count to insert at
        self.update_ui(self.category_combo.currentText())

        # Add the GridLayout to the main layout
        layout.addLayout(self.details_layout)

        # Add button section layout
        button_section = QHBoxLayout()
        button_section.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Add Save button
        self.a_usave = QPushButton("Add")
        self.a_usave.setStyleSheet("font-size: 15px; color: #000000; background-color: #ffffff; border-radius: 10px;")
        self.a_usave.setFixedSize(80, 25)
        self.a_usave.clicked.connect(self.add)
        button_section.addWidget(self.a_usave)

        layout.addLayout(button_section)
        widget.setLayout(layout)
        widget.setStyleSheet("QWidget {background-color: #303030; border-radius: 10px; color: #ffffff; font-size: 15px;}")

        # Add widgets to layout
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def update_ui(self, category):
        if category == 'Lab Assistant':
            self.a_uid.setText(f"LA{self.generate_id()}")
            self.details_layout.addWidget(self.password_label, 5, 1, Qt.AlignmentFlag.AlignVCenter)
            self.details_layout.addWidget(self.a_upassword, 5, 2, Qt.AlignmentFlag.AlignVCenter)
            self.details_layout.addWidget(self.confirm_password_label, 6, 1, Qt.AlignmentFlag.AlignVCenter)
            self.details_layout.addWidget(self.a_uconfirm_password, 6, 2, Qt.AlignmentFlag.AlignVCenter)
        else:
            self.a_uid.setText(f"R{self.generate_id()}")
            self.remove_password_fields()

    def remove_password_fields(self):
        self.details_layout.removeWidget(self.password_label)
        self.details_layout.removeWidget(self.a_upassword)
        self.password_label.setParent(None)
        self.a_upassword.setParent(None)
        self.details_layout.removeWidget(self.confirm_password_label)
        self.details_layout.removeWidget(self.a_uconfirm_password)
        self.confirm_password_label.setParent(None)
        self.a_uconfirm_password.setParent(None)

    def select_image(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.xpm *.jpg)")
        if file_path:
            pixmap = QPixmap(file_path)
            self.user_image.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio))

    def add(self):
        self.main_window.show_user()
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

    def generate_id(self):
        # You might have some logic here to generate a unique ID
        return "0001"
