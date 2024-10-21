from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLineEdit, QGridLayout
)
from PySide6.QtCore import Qt, QSize, QByteArray, QBuffer, QIODevice
from PySide6.QtGui import QPixmap, QPainter, QIntValidator
import qtawesome as qta
import base64
import mysql.connector

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

        #Picture variable
        self.aepic_path = ''

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
        self.a_ename.setStyleSheet("background-color: #484848; color: #ffffff;")
        details_layout.addWidget(self.a_ename, 0, 2, Qt.AlignmentFlag.AlignVCenter)

        # ID Display
        self.a_eid = QLabel()
        self.a_eid.setStyleSheet("color: #ffffff;")
        details_layout.addWidget(self.a_eid, 1, 2, Qt.AlignmentFlag.AlignVCenter)

        # Number Picker for Total (in row 2, column 2)
        num_layout = QHBoxLayout()
        self.a_etotal = QLineEdit("0")
        self.a_etotal.setValidator(QIntValidator())
        self.a_etotal.setFixedSize(50, 30)
        self.a_etotal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.a_etotal.setStyleSheet("background-color: #484848; color: #ffffff; border-radius: 5px;")

        minus_button = QPushButton("-")
        minus_button.setFixedSize(30, 30)
        minus_button.clicked.connect(self.decrease_total)

        plus_button = QPushButton("+")
        plus_button.setFixedSize(30, 30)
        plus_button.clicked.connect(self.increase_total)

        minus_button.setStyleSheet("background-color: #484848; border-top-left-radius: 5px; border-bottom-left-radius: 5px; border-top-right-radius: 0px; border-bottom-right-radius: 0px; color:#ffffff;")
        plus_button.setStyleSheet("background-color: #484848; border-top-left-radius: 0px; border-bottom-left-radius: 0px;  border-top-right-radius: 5px; border-bottom-right-radius: 5px; color:#ffffff;")

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

    def loadaddequipment(self):
        self.equipment_image.setPixmap(QPixmap(self.get_default_image()).scaled(100, 100, Qt.KeepAspectRatio))  # Scale image
        self.equipment_image.setStyleSheet("""border:1px solid #ffffff""")
        self.equipment_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.a_ename.setText('')
        self.a_etotal.setText('0')
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="test"
            )
            cursor = connection.cursor()

            # SQL Query to get the current auto-increment value
            query = """SELECT AUTO_INCREMENT 
                    FROM information_schema.TABLES 
                    WHERE TABLE_SCHEMA = 'test' 
                    AND TABLE_NAME = 'equipment'"""
            cursor.execute(query)

            # Fetch the result (the next auto-increment value)
            result = cursor.fetchone()

            # If there is an auto-increment value, use it; otherwise, start from 1
            if result and result[0] is not None:
                next_id = result[0]
            else:
                next_id = 1

            # Set the equipment ID in the format "E{id:04d}"
            self.a_eid.setText(f"E{next_id:04d}")

        except mysql.connector.Error as e:
            # Handle any SQL or connection errors
            print(f"An error occurred while fetching the next ID: {e}")

        finally:
            # Ensure the connection is closed properly
            if connection:
                connection.close()

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
        self.aepic_path = ''
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.xpm *.jpg)")
        if file_path:
            self.aepic_path = file_path
            pixmap = QPixmap(file_path)
            self.set_rounded_pixmap(self.equipment_image, pixmap)

    def add(self):
        # Get equipment name
        equipment_name = self.a_ename.text()

        # Get total amount
        total_amount = int(self.a_etotal.text())

        # Convert image to a binary format (for storing in database)
        if self.aepic_path:
            image = open(self.aepic_path, 'rb').read()
            encoded_image = base64.b64encode(image)
        else:
            encoded_image = None

        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="test"
            )
            cursor = connection.cursor()

            # SQL Query to insert equipment into the database
            query = """
            INSERT INTO equipment (e_name, e_img, e_amount, e_curr_amount)
            VALUES (%s, %s, %s, %s)
            """
            # Insert current amount equal to total amount initially
            data = (equipment_name, encoded_image, total_amount, total_amount)

            # Execute the SQL query
            cursor.execute(query, data)

            # Commit the transaction
            connection.commit()

        except mysql.connector.Error as e:
            # Handle any SQL or connection errors
            print(f"An error occurred while connecting to the database: {e}")

        finally:
            # Ensure the connection is closed properly
            if connection.is_connected():
                cursor.close()
                connection.close()

        self.main_window.show_equipment()

    def get_default_image(self):
        # Create a default image using a Qt Awesome icon
        icon = qta.icon('fa.file-image-o', color='white')
        pixmap = QPixmap(180, 180)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        icon.paint(painter, pixmap.rect())
        painter.end()
        return pixmap
