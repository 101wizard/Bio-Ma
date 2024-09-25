import sys
import cv2
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QHBoxLayout, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from camera_thread import CameraThread
import base64
import hashlib
import mysql.connector
import re
import time
from src.anti_spoof_predict import AntiSpoofPredict
from src.generate_patches import CropImage
from src.utility import parse_model_name
import face_recognition
import os
import numpy as np

class LoginPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #ADA5A0;")  # Set background color of the main window

        # Create the main layout
        main_layout = QHBoxLayout()

        # Style the VBox layout
        container_widget = QWidget()
        container_widget.setStyleSheet("""
            background-color:  #303030;
            border-radius: 15px;
            padding: 20px;
        """)

        # Create the HBox layout for main content
        login_layout = QHBoxLayout()
        
        # Create a label for the title (or camera display)
        self.camera_display = QLabel(self)
        self.camera_display.setStyleSheet("border:1px solid #ffffff")
        self.camera_display.setFixedWidth(300)
        self.camera_display.setAlignment(Qt.AlignCenter)
        login_layout.addWidget(self.camera_display, 1)

        # Start the camera thread
        self.camera_thread = CameraThread()
        self.camera_thread.frameCaptured.connect(self.update_camera_display)
        self.camera_thread.start()

        # Create the VBox layout for login input
        login_input = QVBoxLayout()

        # Title Label
        title_label = QLabel('Login')  # Assign as instance variable
        title_label.setStyleSheet("""font-family: "Times [Adobe]";
                                          color: #ffffff;
                                          padding: 15px;
                                          font-size: 20px;
                                          font-weight: bold;""")
        login_input.addWidget(title_label)

        # Create input field for UID
        self.uid_input = QLineEdit(self)
        self.uid_input.setPlaceholderText("UID")
        self.uid_input.setStyleSheet("font-size: 15px; color: #000000;")
        login_input.addWidget(self.uid_input)

        # Create input field for password
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("font-size: 15px; color: #000000;")
        login_input.addWidget(self.password_input)

        # Create login button
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login)
        login_button.setStyleSheet("font-size: 15px; color: #000000; background-color: #ffffff; border-radius: 10px;")
        login_input.addWidget(login_button)

        login_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add login input into login layout
        login_layout.addLayout(login_input, 1)
        
        container_widget.setLayout(login_layout)

        # Add VBox layout to the main layout (centered)
        main_layout.addStretch()  # Add space before VBox layout
        main_layout.addWidget(container_widget)
        main_layout.addStretch()  # Add space after VBox layout

        self.setLayout(main_layout)

    def update_camera_display(self, frame):
        # Convert the frame to RGB format for Qt
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = frame.shape
        step = channel * width
        qImg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
        self.camera_display.setPixmap(QPixmap.fromImage(qImg))

        # Save the current frame
        self.current_frame = frame

    def login(self):
        # Check if the current frame is available
        if self.current_frame is None:
            QMessageBox.warning(self, "Error", "No camera frame available for detection.")
            return

        # Pass the captured frame to spoof detection
        label = self.spoof_detection(self.current_frame)

        if label == 1:  # If spoof detection passes
            recognized_user = self.recognize_face(self.current_frame)

            if recognized_user not in ['unknown_person', 'no_persons_found']:
                # Face recognized, proceed to login
                self.camera_thread.stop()
                from main_pg import MainWindow
                self.main_window = MainWindow(recognized_user)  # Pass the recognized user to the main window
                self.main_window.show()
                self.close()
            else:
                # Face not recognized
                QMessageBox.warning(self, "Error", "Face not recognized. Please try again or use UID and Password.")
                self.fallback_to_uid_password()
        else:
            # Spoof detected or face not detected properly
            QMessageBox.warning(self, "Error", "Face spoof detected or no valid face found. Please try again or use UID and Password.")
            self.fallback_to_uid_password()

    def fallback_to_uid_password(self):
        # If face recognition fails, proceed with UID and password authentication
        uid = self.uid_input.text()
        pattern = r'^LA\d{4}$'
        password = self.password_input.text()

        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="test"
            )
            cursor = connection.cursor()

            user_list = []
            
            query = "SELECT la_id, salt, password FROM lab_assistant"
            cursor.execute(query)
            lab_assistant_data = cursor.fetchall()

            for row in lab_assistant_data:
                user_list.append((row[0], row[1], row[2]))  # (id, salt, password)

            if not re.match(pattern, uid):
                QMessageBox.warning(self, "Error", "Invalid UID format")
                return

            intuid = int(uid[2:])

            for lab_assistant_data in lab_assistant_data:
                if intuid != lab_assistant_data[0]:
                    i = 1
                elif intuid == lab_assistant_data[0]:
                    i = 0

                    if lab_assistant_data[2] == hashlib.sha256(lab_assistant_data[1].encode() + password.encode()).hexdigest():
                        self.camera_thread.stop()
                        from main_pg import MainWindow
                        self.main_window = MainWindow(uid)
                        self.main_window.show()
                        self.close()
                        break
                    else:
                        QMessageBox.warning(self, "Error", "Invalid password")
                        break
            if i == 1:
                QMessageBox.warning(self, "Error", "Invalid UID")

        except mysql.connector.Error as e:
            print(f"An error occurred while fetching the user list: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def spoof_detection(self, frame):
        model_dir = 'C:/Users/JQgam/Desktop/Bio-Ma/resources/anti_spoof_models'
        model_test = AntiSpoofPredict(0)
        image_cropper = CropImage()

        frame = cv2.resize(frame, (int(frame.shape[0] * 3 / 4), frame.shape[0]))
        result = self.check_image(frame)

        if result is False:
            return 0  # Spoof detection failed due to invalid image

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
            test_speed += time.time()-start

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
            query = "SELECT la_id, la_img FROM lab_assistant"
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
                    return f"LA{known_face_ids[first_match_index]:04d}"
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


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Show the login page first
    login_page = LoginPage()
    login_page.show()

    sys.exit(app.exec())
