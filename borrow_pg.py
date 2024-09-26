import sys
import cv2
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QHBoxLayout, QMessageBox, QGridLayout, QComboBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from camera_thread import CameraThread
import base64
import mysql.connector
import re
import time
from src.anti_spoof_predict import AntiSpoofPredict
from src.generate_patches import CropImage
from src.utility import parse_model_name
import face_recognition
import os
import numpy as np

class BorrowPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        # Main layout
        main_layout = QVBoxLayout(self)

        # Title Label
        self.title_label = QLabel('Borrow Page')
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

        self.camera_thread = CameraThread()
        self.camera_thread.frameCaptured.connect(self.update_camera_display)
        self.camera_thread.start()

        # Add image to GridLayout in row 0, column 0 (spanning rows)
        self.details_layout.addWidget(self.user_image, 0, 0, 6, 1, Qt.AlignmentFlag.AlignLeft)

        # Name label (auto-updated)
        name_label = QLabel("Name:")
        self.a_uname = QLabel("Waiting for face scan...")  # Initially empty
        self.a_uname.setStyleSheet("color: #ffffff;")
        self.details_layout.addWidget(name_label, 0, 1, Qt.AlignmentFlag.AlignVCenter)
        self.details_layout.addWidget(self.a_uname, 0, 2, Qt.AlignmentFlag.AlignVCenter)

        # User ID label (auto-updated)
        id_label = QLabel("User ID:")
        self.a_uid = QLabel("R0000")  # Default ID
        self.a_uid.setStyleSheet("color: #ffffff;")
        self.details_layout.addWidget(id_label, 1, 1, Qt.AlignmentFlag.AlignVCenter)
        self.details_layout.addWidget(self.a_uid, 1, 2, Qt.AlignmentFlag.AlignVCenter)

        # Phone label (auto-updated)
        phone_label = QLabel("Phone:")
        self.a_uphone = QLabel("Waiting for face scan...")  # Initially empty
        self.a_uphone.setStyleSheet("color: #ffffff;")
        self.details_layout.addWidget(phone_label, 2, 1, Qt.AlignmentFlag.AlignVCenter)
        self.details_layout.addWidget(self.a_uphone, 2, 2, Qt.AlignmentFlag.AlignVCenter)

        # Email label (auto-updated)
        email_label = QLabel("Email:")
        self.a_uemail = QLabel("Waiting for face scan...")  # Initially empty
        self.a_uemail.setStyleSheet("color: #ffffff;")
        self.details_layout.addWidget(email_label, 3, 1, Qt.AlignmentFlag.AlignVCenter)
        self.details_layout.addWidget(self.a_uemail, 3, 2, Qt.AlignmentFlag.AlignVCenter)

        # Add the GridLayout to the main layout
        layout.addLayout(self.details_layout)

        # Add button section layout
        button_section = QHBoxLayout()
        button_section.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Add Save button
        self.a_usave = QPushButton("Add")
        self.a_usave.setStyleSheet("font-size: 15px; color: #000000; background-color: #ffffff; border-radius: 10px;")
        self.a_usave.setFixedSize(80, 25)
        button_section.addWidget(self.a_usave)

        layout.addLayout(button_section)
        widget.setLayout(layout)
        widget.setStyleSheet("QWidget {background-color: #303030; border-radius: 10px; color: #ffffff; font-size: 15px;}")

        # Add widgets to layout
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def recognize_and_update_details(self):
        recognized_user = self.recognize_face(self.current_frame)

        if recognized_user not in ['unknown_person', 'no_persons_found']:
            # Fetch researcher details from the database
            self.fetch_researcher_details(recognized_user)
        else:
            # Clear the fields if not recognized
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
                self.a_uid.setText(f"R{r_id:04d}")
                self.a_uname.setText(r_name)
                self.a_uphone.setText(r_phone)
                self.a_uemail.setText(r_email)
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
        self.a_uid.setText("R0000")
        self.a_uname.setText("Unknown")
        self.a_uphone.setText("Unknown")
        self.a_uemail.setText("Unknown")

    def update_camera_display(self, frame):
        if frame is not None:
            # Convert the frame to RGB format for Qt
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            step = channel * width
            qImg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
            self.user_image.setPixmap(QPixmap.fromImage(qImg))

            # Save the current frame
            self.current_frame = frame

    def recognize_and_update_details(self):
        recognized_user = self.recognize_face(self.current_frame)

        if recognized_user not in ['unknown_person', 'no_persons_found']:
            # Fetch researcher details from the database
            self.fetch_researcher_details(recognized_user)
        else:
            # Clear the fields if not recognized
            self.clear_fields()

    def spoof_detection(self, frame):
        model_dir = 'C:/Users/JQgam/Desktop/Bio-Ma/resources/anti_spoof_models'
        model_test = AntiSpoofPredict(0)
        image_cropper = CropImage()

        frame = cv2.resize(frame, (int(frame.shape[0] * 3 / 4), frame.shape[0]))
        result = self.check_image(frame)

        if result is False:
            return 0  # Spoof detection failed due to invalid image dimensions

        image_bbox = model_test.get_bbox(frame)
        prediction = np.zeros((1, 3))
        test_speed = 0

        for model_name in os.listdir(model_dir):
            h_input, w_input, model_type, scale = parse_model_name(model_name)
            param = {
                "org_img": frame,
                "bbox": image_bbox,
                "scale": scale,
                "out_w": w_input,
                "out_h": h_input,
                "crop": True,
            }
            if scale is None:
                param["crop"] = False
            img = image_cropper.crop(**param)
            start = time.time()
            prediction += model_test.predict(img, os.path.join(model_dir, model_name))
            test_speed += time.time() - start

        label = np.argmax(prediction)
        value = prediction[0][label] / 2

        return label  # Return label, 1 for real, 0 for spoof

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
                    # Return the ID of the first matched face in the format "LAxxxx"
                    first_match_index = matches.index(True)
                    return f"R{known_face_ids[first_match_index]:04d}"
                else:
                    return 'unknown_person'
            else:
                return 'no_persons_found'

        except mysql.connector.Error as e:
            QMessageBox.warning(self, "Database Error", f"An error occurred while fetching face data: {e}")
            return 'unknown_person'

        finally:
            # Ensure the connection is closed properly
            if connection.is_connected():
                cursor.close()
                connection.close()

    def check_image(self, image):
        height, width, channel = image.shape
        if width / height != 3 / 4:
            return False
        else:
            return True