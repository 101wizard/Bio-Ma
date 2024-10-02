from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea,
    QFrame, QSpacerItem, QSizePolicy, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter
import qtawesome as qta 
from RotatedButton import OrientablePushButton
import mysql.connector

class UserPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window 

        # Main layout
        main_layout = QVBoxLayout(self)

        # Title label
        self.label = QLabel("User : Researcher")
        self.label.setStyleSheet("""font-family: "Times [Adobe]";
                                    color: #ffffff;
                                    padding: 15px;
                                    font-size: 20px;
                                    font-weight: bold;""")
        main_layout.addWidget(self.label)

        # Default Signal
        self.current_signal = "R"

        # Main Section
        layout = QHBoxLayout(self)

        # Button layout for switching between Researcher and Lab Assistant
        switch_layout = QVBoxLayout()
        self.researcher_button = OrientablePushButton("Researcher", """OrientablePushButton{
                                                                            background-color: #303030; 
                                                                            border-radius: 0;
                                                                            font-size: 15px;
                                                                            border-top-right-radius: 10px;
                                                                            color: #ffffff;
                                                                            border-left: 0;
                                                                            border-bottom: 1px solid #ffffff;}""")
        self.researcher_button.setFixedWidth(40)
        self.researcher_button.setOrientation(OrientablePushButton.VerticalTopToBottom)
        self.researcher_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.researcher_button.clicked.connect(self.show_researcher)

        self.lab_assistant_button = OrientablePushButton("Lab Assistant", """OrientablePushButton{
                                                                                background-color: #5e8000; 
                                                                                border-radius: 0;
                                                                                font-size: 15px;
                                                                                border-top-left-radius: 10px;
                                                                                color: #ffffff;
                                                                                border-left: 0;
                                                                                border-bottom: 1px solid #ffffff;}
                                                                             OrientablePushButton:hover{
                                                                                background-color: #99cc00;}""")
        self.lab_assistant_button.setFixedWidth(40)
        self.lab_assistant_button.setOrientation(OrientablePushButton.VerticalTopToBottom)
        self.lab_assistant_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.lab_assistant_button.clicked.connect(self.show_lab_assistant)
        
        switch_layout.addWidget(self.researcher_button)
        switch_layout.addWidget(self.lab_assistant_button)
        layout.addLayout(switch_layout)

        # Search bar layout
        search_layout = QHBoxLayout()
        
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search user...")
        self.search_bar.setStyleSheet("font-size: 15px;")
        self.search_bar.textChanged.connect(self.filter_user)  # Connect to search function
        search_layout.addWidget(self.search_bar)

        # Right layout
        vlayout = QVBoxLayout()

        vlayout.addLayout(search_layout)

        # Top border for scroll area
        top_border = QWidget()
        top_border.setFixedHeight(1)
        top_border.setStyleSheet("background-color: #ffffff;")
        vlayout.addWidget(top_border)

        # Label for column headers
        header_frame = QFrame()
        header_frame.setFixedHeight(50)  # Set a fixed height similar to content items
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 0, 20, 0)  # Match margins with content layout
        header_layout.setSpacing(10)  # Match spacing with content layout

        # UID header
        uid_header = QLabel("UID")
        header_layout.addWidget(uid_header)

        # Name header
        name_header = QLabel("Name")
        header_layout.addWidget(name_header)

        # Phone header
        phone_header = QLabel("Phone")
        header_layout.addWidget(phone_header)

        # Email header
        email_header = QLabel("Email")
        header_layout.addWidget(email_header)

        # Detail header
        detail_header = QLabel("Details")
        header_layout.addWidget(detail_header, alignment=Qt.AlignRight)
        
        vlayout.addWidget(header_frame)

        # Scrollable area for list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Hide the vertical scrollbar
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable horizontal scrolling

        self.user_content = QWidget()
        self.user_layout = QVBoxLayout(self.user_content)
        self.user_layout.setContentsMargins(0, 0, 0, 0)
        self.user_layout.setSpacing(20)
        self.user_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area.setWidget(self.user_content)

        vlayout.addWidget(scroll_area)

        # Bottom border for scroll area
        bottom_border = QWidget()
        bottom_border.setFixedHeight(1)
        bottom_border.setStyleSheet("background-color: #ffffff;")
        vlayout.addWidget(bottom_border)

        layout.addLayout(vlayout)

        widget = QWidget()
        widget.setLayout(layout)
        widget.setStyleSheet("""QWidget {
                                        background-color: #303030; 
                                        border-radius: 10px;
                                        color: #ffffff;
                                        font-size: 15px;
                                      }
                                      QPushButton {
                                        border-left: 1px solid #ffffff;
                                        border-radius: 0;
                                        border-top-right-radius: 10px;
                                        border-bottom-right-radius: 10px;
                                      }
                                      QPushButton:hover {
                                        background-color: #383838;
                                      }
                                      """)

        main_layout.addWidget(widget)

        # Adjust the size of the user_content to fit its contents without expanding
        self.user_content.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

    def load_user_pg(self):
        # Default to showing researcher list
        self.user = self.fetch_user_list("R")
        self.show_researcher()

        # Populate list
        self.populate_user_list(self.user, "R")
        
    def show_researcher(self):
        self.label.setText("User : Researcher")
        self.user = self.fetch_user_list("R")
        self.current_signal = "R"  # Update current signal
        self.researcher_button.setStyleSheet("""OrientablePushButton{
                                                    background-color: #303030; 
                                                    border-radius: 0;
                                                    font-size: 15px;
                                                    border-top-right-radius: 10px;
                                                    color: #ffffff;
                                                    border-left: 0;
                                                    border-bottom: 1px solid #ffffff;}""")
        self.lab_assistant_button.setStyleSheet("""OrientablePushButton{
                                                        background-color: #5e8000; 
                                                        border-radius: 0;
                                                        font-size: 15px;
                                                        border-top-left-radius: 10px;
                                                        color: #ffffff;
                                                        border-left: 0;
                                                        border-bottom: 1px solid #ffffff;}
                                                    OrientablePushButton:hover{
                                                        background-color: #99cc00;}""")
        self.populate_user_list(self.user, self.current_signal)

    def show_lab_assistant(self):
        self.label.setText("User : Lab Assistant")
        self.user = self.fetch_user_list("LA")
        self.current_signal = "LA"  # Update current signal
        self.researcher_button.setStyleSheet("""OrientablePushButton{
                                                    background-color: #5e8000; 
                                                    border-radius: 0;
                                                    font-size: 15px;
                                                    border-top-right-radius: 10px;
                                                    color: #ffffff;
                                                    border-left: 0;
                                                    border-bottom: 1px solid #ffffff;}
                                                OrientablePushButton:hover{
                                                    background-color: #99cc00;}""")
        self.lab_assistant_button.setStyleSheet("""OrientablePushButton{
                                                        background-color: #303030; 
                                                        border-radius: 0;
                                                        font-size: 15px;
                                                        border-top-left-radius: 10px;
                                                        color: #ffffff;
                                                        border-left: 0;
                                                        border-bottom: 1px solid #ffffff;}""")
        self.populate_user_list(self.user, self.current_signal)

    def fetch_user_list(self, signal):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="test"
            )
            cursor = connection.cursor()

            user_list = []

            if signal == "R":
                # SQL Query to fetch researcher data
                query = "SELECT r_id, r_name, r_phone, r_email FROM researcher"
                cursor.execute(query)

                # Fetch all the results
                researcher_data = cursor.fetchall()

                # Prepare the researcher list in the desired format
                for row in researcher_data:
                    user_list.append((row[0], row[1], row[2], row[3]))  # (id, name, phone, email)
            
            elif signal == "LA":
                # SQL Query to fetch lab assistant data
                query = "SELECT la_id, la_name, la_phone, la_email FROM lab_assistant"
                cursor.execute(query)

                # Fetch all the results
                lab_assistant_data = cursor.fetchall()

                # Prepare the lab assistant list in the desired format
                for row in lab_assistant_data:
                    user_list.append((row[0], row[1], row[2], row[3]))  # (id, name, phone, email)
            
            return user_list

        except mysql.connector.Error as e:
            # Handle any SQL or connection errors
            print(f"An error occurred while fetching the user list: {e}")
            return []

        finally:
            # Ensure the connection is closed properly
            if connection.is_connected():
                cursor.close()
                connection.close()

    def populate_user_list(self, user_list, signal):
        # Clear existing items
        while self.user_layout.count() > 0: 
            item = self.user_layout.takeAt(0)  # Take the first item
            if item.widget():  # If the item is a widget
                item.widget().deleteLater()  # Delete the widget

        # Add items to layout
        for uid, name, phone, email in user_list:
            formatted_id = f"R{uid:04d}" if signal == "R" else f"LA{uid:04d}"
            self.add_user(formatted_id, name, phone, email)

    def add_user(self, uid, name, phone, email):
        item_frame = QFrame()
        item_frame.setFixedHeight(100)  # Consistent height for each item
        layout = QVBoxLayout(item_frame)
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(10, 0, 10, 0)
        item_layout.setSpacing(10)

        # UID
        uid_label = QLabel(uid)
        item_layout.addWidget(uid_label)

        # Name
        name_label = QLabel(name)
        item_layout.addWidget(name_label)

        # Phone
        phone_label = QLabel(phone)
        item_layout.addWidget(phone_label)

        # Email
        email_label = QLabel(email)
        item_layout.addWidget(email_label)

        # View button
        view_button = QPushButton("View")
        view_button.setStyleSheet("text-decoration: underline;")
        view_button.setFixedSize(50, 80)
        view_button.clicked.connect(lambda: self.show_view_user_page(uid))
        
        # Add the button to the right side
        item_layout.addWidget(view_button, alignment=Qt.AlignRight | Qt.AlignTop)

        layout.addLayout(item_layout)

        # Add the frame to the layout
        self.user_layout.addWidget(item_frame)

        # Add a separator line below the item frame
        line = QFrame()
        line.setLineWidth(1)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Plain)
        line.setStyleSheet("background-color: #ffffff;")  # Ensure the color is white and visible
        line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        line.setFixedHeight(1)

        # Add the separator line after the item frame
        self.user_layout.addWidget(line)

    def show_view_user_page(self, uid):
        self.main_window.user_details.update_content(user_id=uid, title=self.label.text())
        self.main_window.stacked_widget.setCurrentWidget(self.main_window.user_details)
        print(f"Viewing User ID: {uid}")

    def filter_user(self):
        search_text = self.search_bar.text().lower()
        # Filter the list based on the current search text
        filtered_user = (
            [item for item in self.user if search_text in item[1].lower()]
            if search_text  # If there is text in the search bar
            else self.user  # If search bar is empty, show all items
        )
        self.populate_user_list(filtered_user, self.current_signal)  # Pass the current signal
