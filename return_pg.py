import sys
import cv2
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QGridLayout, QMessageBox, QPushButton
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from camera_thread import CameraThread
import base64
import mysql.connector
import face_recognition
import numpy as np

class ReturnPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.recognized_user_id = None  # To store the recognized researcher ID

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

        # User image
        self.user_image = QLabel(self)
        self.user_image.setFixedSize(500, 500)
        self.user_image.setStyleSheet("border:1px solid #ffffff")
        self.user_image.setAlignment(Qt.AlignCenter)

        # Add image to GridLayout in row 0, column 0 (spanning rows)
        self.details_layout.addWidget(self.user_image, 0, 0, 6, 1, Qt.AlignmentFlag.AlignLeft)

        # Name label (auto-updated)
        name_label = QLabel("Name:")
        self.rname = QLabel("Waiting for face scan...")  # Initially empty
        self.rname.setStyleSheet("color: #ffffff;")
        self.details_layout.addWidget(name_label, 0, 1, Qt.AlignmentFlag.AlignVCenter)
        self.details_layout.addWidget(self.rname, 0, 2, Qt.AlignmentFlag.AlignVCenter)

        # User ID label (auto-updated)
        id_label = QLabel("User ID:")
        self.rid = QLabel("R0000")  # Default ID
        self.rid.setStyleSheet("color: #ffffff;")
        self.details_layout.addWidget(id_label, 1, 1, Qt.AlignmentFlag.AlignVCenter)
        self.details_layout.addWidget(self.rid, 1, 2, Qt.AlignmentFlag.AlignVCenter)

        # Phone label (auto-updated)
        phone_label = QLabel("Phone:")
        self.rphone = QLabel("Waiting for face scan...")  # Initially empty
        self.rphone.setStyleSheet("color: #ffffff;")
        self.details_layout.addWidget(phone_label, 2, 1, Qt.AlignmentFlag.AlignVCenter)
        self.details_layout.addWidget(self.rphone, 2, 2, Qt.AlignmentFlag.AlignVCenter)

        # Email label (auto-updated)
        email_label = QLabel("Email:")
        self.remail = QLabel("Waiting for face scan...")  # Initially empty
        self.remail.setStyleSheet("color: #ffffff;")
        self.details_layout.addWidget(email_label, 3, 1, Qt.AlignmentFlag.AlignVCenter)
        self.details_layout.addWidget(self.remail, 3, 2, Qt.AlignmentFlag.AlignVCenter)

        # Print button
        self.print_button = QPushButton("Print Detected ID")
        self.print_button.setFixedWidth(160)
        self.print_button.clicked.connect(self.print_detected_id)
        self.print_button.setStyleSheet("background-color: #ffffff; font-size: 16px; padding: 10px; border-radius: 5px;")
        self.details_layout.addWidget(self.print_button, 4, 2, Qt.AlignmentFlag.AlignCenter)

        # Add the GridLayout to the main layout
        layout.addLayout(self.details_layout)

        widget.setLayout(layout)
        widget.setStyleSheet("QWidget {background-color: #303030; border-radius: 10px; color: #ffffff; font-size: 15px;}")

        # Add widgets to layout
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Timer for continuous face recognition
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.recognize_and_update_details)
        self.timer.start(1000)  # Trigger every second for face detection

    def loadreturnpage(self):
        self.clear_fields()
        self.main_window.camera_thread.frameCaptured.connect(self.update_camera_display)
        self.main_window.current_signal_handler = self.update_camera_display
        self.main_window.current_signal_page = 'R'
        self.timer.start(1000)

    def unloadreturnpage(self):
        self.timer.stop()
        self.main_window.current_signal_page = ''

    def recognize_and_update_details(self):
        if hasattr(self, 'current_frame'):
            recognized_user = self.recognize_face(self.current_frame)

            if recognized_user not in ['unknown_person', 'no_persons_found']:
                # Store the recognized user ID
                self.recognized_user_id = recognized_user

                # Fetch researcher details from the database
                self.fetch_researcher_details(recognized_user)
            else:
                # Clear the fields if no face is recognized
                self.clear_fields()

    def fetch_researcher_details(self, researcher_id):
        try:
            # Connect to the database
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="test"
            )
            cursor = connection.cursor()

            # Query to get researcher details from the database
            query = "SELECT r_id, r_name, r_phone, r_email FROM researcher WHERE r_id = %s"
            cursor.execute(query, (researcher_id,))
            result = cursor.fetchone()

            if result:
                r_id, r_name, r_phone, r_email = result
                # Update the fields
                self.rid.setText(f"R{r_id:04d}")
                self.rname.setText(r_name)
                self.rphone.setText(r_phone)
                self.remail.setText(r_email)
            else:
                # Clear the fields if no matching record is found
                self.clear_fields()

        except mysql.connector.Error as e:
            QMessageBox.warning(self, "Database Error", f"An error occurred while fetching data: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def clear_fields(self):
        # Clear all fields when face recognition fails
        self.rname.setText("Waiting for face scan...")
        self.rid.setText("R0000")
        self.rphone.setText("Waiting for face scan...")
        self.remail.setText("Waiting for face scan...")

    def update_camera_display(self, frame):
        if frame is not None:
            # Convert the frame to RGB format for Qt
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            step = channel * width
            qImg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
            self.user_image.setPixmap(QPixmap.fromImage(qImg))

            # Save the current frame for future face recognition
            self.current_frame = frame

    def recognize_face(self, frame):
        try:
            # Connect to the database
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="test"
            )
            cursor = connection.cursor()

            # Query to get all face encodings from the database (stored as BLOB)
            query = "SELECT r_id, r_img FROM researcher"
            cursor.execute(query)

            known_face_encodings = []
            known_face_ids = []

            for (la_id, la_img) in cursor.fetchall():
                # Convert the BLOB data (base64 string) back to an image
                img_data = base64.b64decode(la_img)  # Decode base64 to bytes
                np_array = np.frombuffer(img_data, np.uint8)  # Convert bytes to numpy array
                img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)  # Decode image to OpenCV format

                # Get the face encoding from the image
                face_encoding = face_recognition.face_encodings(img)[0]  # Assuming one face per image
                known_face_encodings.append(face_encoding)
                known_face_ids.append(la_id)

            # Ensure the current frame contains at least one face
            if len(face_recognition.face_encodings(frame)) > 0:
                unknown_face_encoding = face_recognition.face_encodings(frame)[0]

                # Compare the captured face with known faces from the database
                matches = face_recognition.compare_faces(known_face_encodings, unknown_face_encoding)

                if True in matches:
                    # Return the ID of the first matched face in the format LAxxxx
                    match_index = matches.index(True)
                    return known_face_ids[match_index]
                else:
                    return 'unknown_person'
            else:
                return 'no_persons_found'

        except mysql.connector.Error as e:
            QMessageBox.warning(self, "Database Error", f"An error occurred while fetching data: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def print_detected_id(self):
        if self.recognized_user_id:
            print(f"Detected Researcher ID: {self.recognized_user_id}")
        else:
            QMessageBox.warning(self, "Error", "No researcher detected.")

        