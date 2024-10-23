from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLineEdit, QGridLayout, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, QSize, QBuffer, QIODevice, QEventLoop
from PySide6.QtGui import QPixmap, QPainter, QImage
from PySide6.QtMultimedia import QCamera, QImageCapture, QMediaDevices
import qtawesome as qta
from camera_thread import CameraThread
import cv2
import mysql.connector
import base64
import random
import string
import re
import hashlib

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

        # User image
        self.user_image = QLabel(self)
        self.user_image.setFixedSize(500, 500)
        self.user_image.setStyleSheet("border:1px solid #ffffff")
        self.user_image.setAlignment(Qt.AlignCenter)

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
        self.a_uname.setStyleSheet("background-color: #484848; color: #ffffff;")
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
        self.a_uphone.setStyleSheet("background-color: #484848; color: #ffffff;")
        self.details_layout.addWidget(phone_label, 3, 1, Qt.AlignmentFlag.AlignVCenter)
        self.details_layout.addWidget(self.a_uphone, 3, 2, Qt.AlignmentFlag.AlignVCenter)

        # Email Input
        email_label = QLabel("Email:")
        self.a_uemail = QLineEdit()
        self.a_uemail.setStyleSheet("background-color: #484848; color: #ffffff;")
        self.details_layout.addWidget(email_label, 4, 1, Qt.AlignmentFlag.AlignVCenter)
        self.details_layout.addWidget(self.a_uemail, 4, 2, Qt.AlignmentFlag.AlignVCenter)

        # Password Input
        self.password_label = QLabel("Password:")
        self.a_upassword = QLineEdit()
        self.a_upassword.setEchoMode(QLineEdit.Password)
        self.a_upassword.setStyleSheet("background-color: #484848; color: #ffffff;")

        # Confirm Password Input
        self.confirm_password_label = QLabel("Confirm Password:")
        self.a_uconfirm_password = QLineEdit()
        self.a_uconfirm_password.setEchoMode(QLineEdit.Password)
        self.a_uconfirm_password.setStyleSheet("background-color: #484848; color: #ffffff;")

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
        self.a_usave.clicked.connect(lambda: self.add(self.category_combo.currentText()))
        button_section.addWidget(self.a_usave)

        layout.addLayout(button_section)
        widget.setLayout(layout)
        widget.setStyleSheet("QWidget {background-color: #303030; border-radius: 10px; color: #ffffff; font-size: 15px;}")

        # Add widgets to layout
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def loadadduser(self):
        self.category_combo.setCurrentIndex(0)
        self.a_uname.setText('')
        self.a_uemail.setText('')
        self.a_upassword.setText('')
        self.a_uphone.setText('')
        self.a_uconfirm_password.setText('')
        self.main_window.camera_thread.frameCaptured.connect(self.update_camera_display)
        self.main_window.current_signal_handler = self.update_camera_display
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
                    AND TABLE_NAME = 'researcher'"""
            cursor.execute(query)

            # Fetch the result (the next auto-increment value)
            result = cursor.fetchone()

            # If there is an auto-increment value, use it; otherwise, start from 1
            if result and result[0] is not None:
                next_id = result[0]
            else:
                next_id = 1

            # Set the researcher ID in the format "R{id:04d}"
            self.a_uid.setText(f"R{next_id:04d}")

        except mysql.connector.Error as e:
            # Handle any SQL or connection errors
            print(f"An error occurred while fetching the next ID: {e}")

        finally:
            # Ensure the connection is closed properly
            if connection:
                connection.close()

    def update_ui(self, category):
        if category == 'Lab Assistant':
            self.a_uid.setText(f"LA{self.generate_id('LA'):04d}")
            self.details_layout.addWidget(self.password_label, 5, 1, Qt.AlignmentFlag.AlignVCenter)
            self.details_layout.addWidget(self.a_upassword, 5, 2, Qt.AlignmentFlag.AlignVCenter)
            self.details_layout.addWidget(self.confirm_password_label, 6, 1, Qt.AlignmentFlag.AlignVCenter)
            self.details_layout.addWidget(self.a_uconfirm_password, 6, 2, Qt.AlignmentFlag.AlignVCenter)
        else:
            self.a_uid.setText(f"R{self.generate_id('R'):04d}")
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

    def add(self, role):
        print(role)
        # Get user name
        user_name = self.a_uname.text()
        # Get user email
        user_email = self.a_uemail.text()
        # Get user phone
        user_phone = self.a_uphone.text()

        if not user_name:
            QMessageBox.warning(self, 'Error', 'Please enter Username!')
            return
        if not user_email or not re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', user_email):
            QMessageBox.warning(self, 'Error', 'Please enter a valid email address!')
            return
        if not user_phone:
            QMessageBox.warning(self, 'Error', 'Please enter Phone Number!')
            return

        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="test"
            )
            cursor = connection.cursor()

            if role == 'Lab Assistant':
                # Get user password
                password = self.a_upassword.text()
                # Get user confirmpassword
                confirmpassword = self.a_uconfirm_password.text()

                if password != confirmpassword:
                    QMessageBox.warning(self, 'Error', 'Password does not match!')
                    return
                if len(password) < 8 or len(password) > 18:
                    QMessageBox.warning(self, 'Error', 'Password should be between 8 and 18 characters!')
                    return 
                # Check for at least one lowercase letter
                if not any(c.islower() for c in password):
                    QMessageBox.warning(self, 'Error', 'Password should contain at least one lowercase letter!')
                    return 
                # Check for at least one uppercase letter
                if not any(c.isupper() for c in password):
                    QMessageBox.warning(self, 'Error', 'Password should contain at least one uppercase letter!')
                    return
                # Check for at least one digit
                if not any(c.isdigit() for c in password):
                    QMessageBox.warning(self, 'Error', 'Password should contain at least one lowercase letter!')
                    return
                # Check for any spaces
                if any(c.isspace() for c in password):
                    QMessageBox.warning(self, 'Error', 'Password should not contain any spaces!')
                    return 
                # Check for unrecognized characters (e.g., special characters)
                special_characters = string.punctuation
                if not any(c in special_characters for c in password):
                    QMessageBox.warning(self, 'Error', 'Password should contain at least one special character!')
                    return 
                
                salt = self.generate_random_characters()
                encoded_password = hashlib.sha256(salt.encode() + password.encode()).hexdigest()
                encoded_image = self.capture_image()
            
                # SQL Query to insert equipment into the database
                query = """
                INSERT INTO lab_assistant (la_name, la_phone, la_email, la_img, salt, password)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                # Insert current amount equal to total amount initially
                data = (user_name, user_phone, user_email, encoded_image, salt, encoded_password)
            else:
                encoded_image = self.capture_image()
                # SQL Query to insert equipment into the database
                query = """
                INSERT INTO researcher (r_name, r_phone, r_email, r_img)
                VALUES (%s, %s, %s, %s)
                """
                # Insert current amount equal to total amount initially
                data = (user_name, user_phone, user_email, encoded_image)

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
        
        self.main_window.show_user()

    def generate_id(self, role):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="test"
            )
            cursor = connection.cursor()

            if role == 'R':
                # SQL Query to get the current auto-increment value
                query = """SELECT AUTO_INCREMENT 
                        FROM information_schema.TABLES 
                        WHERE TABLE_SCHEMA = 'test' 
                        AND TABLE_NAME = 'researcher'"""
                cursor.execute(query)
            else:
                # SQL Query to get the current auto-increment value
                query = """SELECT AUTO_INCREMENT 
                        FROM information_schema.TABLES 
                        WHERE TABLE_SCHEMA = 'test' 
                        AND TABLE_NAME = 'lab_assistant'"""
                cursor.execute(query)

            # Fetch the result (the next auto-increment value)
            result = cursor.fetchone()

            # If there is an auto-increment value, use it; otherwise, start from 1
            if result and result[0] is not None:
                next_id = result[0]
            else:
                next_id = 1

        except mysql.connector.Error as e:
            # Handle any SQL or connection errors
            print(f"An error occurred while fetching the next ID: {e}")

        finally:
            # Ensure the connection is closed properly
            if connection:
                connection.close()

            #return the value
            return next_id
    
    def update_camera_display(self, frame):
        # Convert the frame to RGB format for Qt
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = frame.shape
        step = channel * width
        qImg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
        self.user_image.setPixmap(QPixmap.fromImage(qImg))

    def capture_image(self):
        self.main_window.camera_thread.stop()
        cap = cv2.VideoCapture(0)  # Use the appropriate camera index (0, 1, etc.)
        
        if not cap.isOpened():
            QMessageBox.warning(self, 'Error', 'Could not open camera!')
            return

        ret, frame = cap.read()  # Capture a frame
        cap.release()  # Release the camera

        if not ret:
            QMessageBox.warning(self, 'Error', 'Failed to capture image!')
            return

        # Encode image to base64
        _, buffer = cv2.imencode('.jpg', frame)  # Encode as JPEG
        img_bytes = buffer.tobytes()  # Convert to bytes
        encoded_image = base64.b64encode(img_bytes).decode('utf-8')  # Convert to base64 string

        self.main_window.start_camera()

        return encoded_image

    def generate_random_characters(self):
        # Combine uppercase letters and digits
        characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
        # Generate a random selection of the combined characters
        random_characters = ''.join(random.choices(characters, k=30))
        return random_characters
