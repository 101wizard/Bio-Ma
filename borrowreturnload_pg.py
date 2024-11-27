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
import datetime

class BorrowReturnLoadPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.recognized_user_id = None  # To store the recognized researcher ID
        self.current_page = None  # Tracks if we're on Borrow or Return page

        # Main layout
        main_layout = QVBoxLayout(self)

        # Title Label
        self.title_label = QLabel('')
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

        # Name label 
        name_label = QLabel("Name:")
        self.rname = QLabel("Waiting for face scan...")  # Initially empty
        self.rname.setStyleSheet("color: #ffffff;")
        self.details_layout.addWidget(name_label, 0, 1, Qt.AlignmentFlag.AlignVCenter)
        self.details_layout.addWidget(self.rname, 0, 2, Qt.AlignmentFlag.AlignVCenter)

        # User ID label 
        id_label = QLabel("User ID:")
        self.rid = QLabel("R0000")  # Default ID
        self.rid.setStyleSheet("color: #ffffff;")
        self.details_layout.addWidget(id_label, 1, 1, Qt.AlignmentFlag.AlignVCenter)
        self.details_layout.addWidget(self.rid, 1, 2, Qt.AlignmentFlag.AlignVCenter)

        # Phone label 
        phone_label = QLabel("Phone:")
        self.rphone = QLabel("Waiting for face scan...")  # Initially empty
        self.rphone.setStyleSheet("color: #ffffff;")
        self.details_layout.addWidget(phone_label, 2, 1, Qt.AlignmentFlag.AlignVCenter)
        self.details_layout.addWidget(self.rphone, 2, 2, Qt.AlignmentFlag.AlignVCenter)

        # Email label 
        email_label = QLabel("Email:")
        self.remail = QLabel("Waiting for face scan...")  # Initially empty
        self.remail.setStyleSheet("color: #ffffff;")
        self.details_layout.addWidget(email_label, 3, 1, Qt.AlignmentFlag.AlignVCenter)
        self.details_layout.addWidget(self.remail, 3, 2, Qt.AlignmentFlag.AlignVCenter)

        # Borrow label 
        borrow_label = QLabel("Borrow List:")
        self.rborrow = QLabel("Waiting for face scan...")  # Initially empty
        self.rborrow.setStyleSheet("color: #ffffff;")
        self.details_layout.addWidget(borrow_label, 4, 1, Qt.AlignmentFlag.AlignVCenter)
        self.details_layout.addWidget(self.rborrow, 4, 2, Qt.AlignmentFlag.AlignVCenter)

        # Scan button
        self.scan_button = QPushButton("Scan")
        self.scan_button.setFixedWidth(160)
        self.scan_button.clicked.connect(self.scan_for_user)
        self.scan_button.setStyleSheet("background-color: #ffffff; color:#000000; font-size: 16px; padding: 10px; border-radius: 5px;")
        self.details_layout.addWidget(self.scan_button, 5, 1, Qt.AlignmentFlag.AlignCenter)

        # Confirm button
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.setFixedWidth(160)
        self.confirm_button.setEnabled(False) # Initially hidden
        self.confirm_button.setStyleSheet("""QPushButton {
                                            background-color: #ffffff;
                                            color: #000000;
                                            font-size: 16px;
                                            padding: 10px;
                                            border-radius: 5px;
                                        }
                                        QPushButton:disabled {
                                            background-color: #cccccc;
                                            color: #888888; 
                                            border: 1px solid #aaaaaa;  
                                        }""")
        self.details_layout.addWidget(self.confirm_button, 5, 2, Qt.AlignmentFlag.AlignCenter)


        # Add the GridLayout to the main layout
        layout.addLayout(self.details_layout)

        widget.setLayout(layout)
        widget.setStyleSheet("QWidget {background-color: #303030; border-radius: 10px; color: #ffffff; font-size: 15px;}")

        # Add widgets to layout
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def loadborrowreturnpage(self, action):
        self.clear_fields()
        self.main_window.camera_thread.frameCaptured.connect(self.update_camera_display)
        self.main_window.current_signal_handler = self.update_camera_display
        self.current_page = action
        self.confirm_button.setEnabled(False)
        self.title_label.setText(action)

    def scan_for_user(self):
        if hasattr(self, 'current_frame'):
            recognized_user = self.recognize_face(self.current_frame)

            if recognized_user not in ['unknown_person', 'no_persons_found']:
                # Store the recognized user ID
                self.recognized_user_id = recognized_user

                # Fetch researcher details from the database
                self.fetch_researcher_details(recognized_user)

                # Fetch specific researcher borrow list from database
                self.fetch_borrow_details(recognized_user)
                
                # Print the recognized user ID
                print(f"Detected Researcher ID: {self.recognized_user_id}")

                if self.current_page == 'Return':
                    self.handle_return_scan(recognized_user)
                elif self.current_page == 'Borrow':
                    self.handle_borrow_scan(recognized_user)
            else:
                # Clear the fields if no face is recognized
                self.clear_fields()
                self.confirm_button.setEnabled(False)
                QMessageBox.warning(self, "Error", "No face detected or unknown user.")

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

            for (r_id, r_img) in cursor.fetchall():
                # Convert the BLOB data (base64 string) back to an image
                img_data = base64.b64decode(r_img)  # Decode base64 to bytes
                np_array = np.frombuffer(img_data, np.uint8)  # Convert bytes to numpy array
                img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)  # Decode image to OpenCV format

                # Get the face encoding from the image (check if encoding exists)
                face_encodings = face_recognition.face_encodings(img)
                if len(face_encodings) > 0:
                    face_encoding = face_encodings[0]
                    known_face_encodings.append(face_encoding)
                    known_face_ids.append(r_id)
                else:
                    print(f"No face detected in researcher image with ID {r_id}")

            # Ensure the current frame contains at least one face
            unknown_face_encodings = face_recognition.face_encodings(frame)
            if len(unknown_face_encodings) > 0:
                unknown_face_encoding = unknown_face_encodings[0]

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

    def fetch_borrow_details(self, researcher_id):
        try:
            connection = mysql.connector.connect(host="localhost", user="root", password="", database="test")
            cursor = connection.cursor()

            # Query to get borrow details
            query = "SELECT borrow_id, due_date FROM borrow WHERE r_id = %s"
            cursor.execute(query, (researcher_id,))
            borrow_details = cursor.fetchall()

            if borrow_details:
                borrow_info = ""
                for borrow_id, due_date in borrow_details:
                    formatted_date = due_date.strftime('%Y-%m-%d')
                    overdue = due_date < datetime.datetime.now()
                    if overdue:
                        borrow_info += f"<span style='color: red;'>Borrow ID {borrow_id} - Due {formatted_date}</span><br>"
                    else:
                        borrow_info += f"Borrow ID {borrow_id} - Due {formatted_date}<br>"
                self.rborrow.setText(borrow_info)
            else:
                self.rborrow.setText("No pending returns")

        except mysql.connector.Error as e:
            QMessageBox.warning(self, "Database Error", f"An error occurred while fetching data: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def handle_return_scan(self, researcher_id):
        try:
            connection = mysql.connector.connect(host="localhost", user="root", password="", database="test")
            cursor = connection.cursor()

            # Check if the user has pending returns
            query = "SELECT COUNT(*) FROM borrow WHERE r_id = %s"
            cursor.execute(query, (researcher_id,))
            pending_return = cursor.fetchone()[0] > 0

            if pending_return:
                self.confirm_button.setEnabled(True)
                self.confirm_button.clicked.connect(self.navigate_to_return_pg)
            else:
                self.confirm_button.setEnabled(False)

        except mysql.connector.Error as e:
            QMessageBox.warning(self, "Database Error", f"An error occurred while fetching data: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def handle_borrow_scan(self, researcher_id):
        try:
            connection = mysql.connector.connect(host="localhost", user="root", password="", database="test")
            cursor = connection.cursor()

            # Check if there are overdue returns
            query = "SELECT due_date FROM borrow WHERE r_id = %s"
            cursor.execute(query, (researcher_id,))
            borrow_due_dates = cursor.fetchall()

            has_overdue = any(due_date.date() <= datetime.datetime.now().date() for due_date, in borrow_due_dates)

            if has_overdue:
                self.confirm_button.setEnabled(False)
            else:
                self.confirm_button.setEnabled(True)
            self.confirm_button.clicked.connect(self.navigate_to_borrow_pg)

        except mysql.connector.Error as e:
            QMessageBox.warning(self, "Database Error", f"An error occurred while fetching data: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def navigate_to_return_pg(self):
        # Navigate to the return page
        self.main_window.return_page.loadreturnpage(self.recognized_user_id)
        self.main_window.stacked_widget.setCurrentWidget(self.main_window.return_page)

    def navigate_to_borrow_pg(self):
        # Navigate to the borrow page
        self.main_window.borrow_page.loadborrowpage(self.recognized_user_id)
        self.main_window.stacked_widget.setCurrentWidget(self.main_window.borrow_page)
        
    def clear_fields(self):
        # Clear all fields when face recognition fails
        self.rname.setText("Waiting for face scan...")
        self.rid.setText("R0000")
        self.rphone.setText("Waiting for face scan...")
        self.remail.setText("Waiting for face scan...")
        self.rborrow.setText("Waiting for face scan...")

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
