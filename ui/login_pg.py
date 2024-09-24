import sys
import cv2
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from camera_thread import CameraThread

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

    def login(self):
        uid = self.uid_input.text()
        if uid:
            self.camera_thread.stop()  # Stop the camera thread
            from main_pg import MainWindow
            self.main_window = MainWindow(uid)  # Pass the UID to the main window
            self.main_window.show()
            self.close()  # Close the login window

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Show the login page first
    login_page = LoginPage()
    login_page.show()

    sys.exit(app.exec())
