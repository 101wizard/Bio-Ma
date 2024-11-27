from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea,
    QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
import mysql.connector

class DashboardPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window 

        # Main layout
        main_layout = QVBoxLayout(self)

        # Label
        label = QLabel("Dashboard")
        label.setStyleSheet("""font-family: "Times [Adobe]";
                                color: #ffffff;
                                padding: 15px;
                                font-size: 20px;
                                font-weight: bold;""")

        # Main Section
        layout = QHBoxLayout(self)
        
        # Left side layout for buttons
        left_layout = QVBoxLayout()

        # Return button
        return_button = QPushButton("Return")
        return_button.setStyleSheet("""QPushButton {
                                            background-color: #303030; 
                                            border-radius: 10px;
                                            font-size: 20px;
                                            color: #ffffff;
                                        }
                                        QPushButton:hover {
                                            background-color: #383838;
                                        }""")
        return_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return_button.clicked.connect(self.show_return_page)
        left_layout.addWidget(return_button, 1)

        # Borrow button
        borrow_button = QPushButton("Borrow")
        borrow_button.setStyleSheet("""QPushButton {
                                            background-color: #303030; 
                                            border-radius: 10px;
                                            font-size: 20px;
                                            color: #ffffff;
                                        }
                                        QPushButton:hover {
                                            background-color: #383838;
                                        }""")
        borrow_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        borrow_button.clicked.connect(self.show_borrow_page)
        left_layout.addWidget(borrow_button, 1)

        layout.addLayout(left_layout)

        # Right side layout
        right_layout = QVBoxLayout()

        # Right side layout for notifications
        notification_layout = QVBoxLayout()

        # Notification Label
        notification_label = QLabel("NOTIFICATION")
        notification_label.setStyleSheet("font-weight: bold; font-size: 20px; padding: 5px;")
        notification_layout.addWidget(notification_label)

        # Top border
        top_border = QWidget()
        top_border.setFixedHeight(1)
        top_border.setStyleSheet("background-color: #ffffff; border-radius: 10px;")
        notification_layout.addWidget(top_border)

        # Scrollable area for notifications (vertically)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable horizontal scrolling
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Hide the vertical scrollbar
        notification_content = QWidget()
        notification_layout_inside = QVBoxLayout(notification_content)
        notification_layout_inside.setContentsMargins(0, 0, 0, 0)
        notification_layout_inside.setSpacing(10)
        notification_layout_inside.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area.setWidget(notification_content)
        notification_layout.addWidget(scroll_area)

        # Bottom border
        bottom_border = QWidget()
        bottom_border.setFixedHeight(1)
        bottom_border.setStyleSheet("background-color: #ffffff; border-radius: 10px;")
        notification_layout.addWidget(bottom_border)

        # Convert layout into widget
        right_widget = QWidget()
        right_widget.setLayout(notification_layout)
        right_widget.setStyleSheet("""QWidget {
                                        background-color: #303030; 
                                        border-radius: 10px;
                                        color: #ffffff;
                                      }
                                      QPushButton {
                                        border-left: 1px solid #ffffff;
                                        border-radius: 0;
                                        border-top-right-radius: 10px;
                                        border-bottom-right-radius: 10px;
                                      }
                                      QPushButton:hover {
                                        background-color: #383838;
                                      }""")
        right_widget.setMaximumWidth(500)
        right_widget.setMinimumWidth(400)
        
        # Add widget to layout
        right_layout.addWidget(right_widget)
        
        # notifications
        notifications = self.fetch_notification()
        
        for entity, due_date, curr_date_time in notifications:
            status_text = self.generate_notification_status(due_date, curr_date_time)
            self.add_notification(notification_layout_inside, entity, status_text, due_date)

        layout.addLayout(right_layout)

        main_layout.addWidget(label)
        main_layout.addLayout(layout)

    def fetch_notification(self):
        try:
            # Step 1: Connect to the database
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="test"
            )
            cursor = connection.cursor()

            # Prepare the query to fetch only researchers with due items
            query = """
                SELECT researcher.r_id, researcher.r_name, borrow.due_date, NOW()
                FROM borrow
                JOIN researcher ON borrow.r_id = researcher.r_id
                WHERE DATE(borrow.due_date) <= DATE(NOW())
            """
            
            # Execute the query
            cursor.execute(query)
            
            # Fetch all the results
            results = cursor.fetchall()

            # Format the data into the desired format
            notifications = [
                (f"R{r_id:04d} : {r_name}", due_date.strftime("%d/%m/%Y"), current_date_time.strftime("%d/%m/%Y %I:%M %p"))
                for r_id, r_name, due_date, current_date_time in results
            ]
            
            return notifications

        except mysql.connector.Error as e:
            # Handle database errors
            print(f"Error: {e}")
            return []  # Return an empty list in case of an error

        finally:
            # Ensure the connection is closed properly
            if connection.is_connected():
                cursor.close()
                connection.close()

    def generate_notification_status(self, due_date, curr_date_time):
        # Logic to determine notification status
        due_date_obj = self.parse_date(due_date)
        curr_date_obj = self.parse_date(curr_date_time.split()[0])  # only use the date part

        if due_date_obj == curr_date_obj:
            return "have items due today!"
        elif due_date_obj < curr_date_obj:
            return "have unreturned overdue items!"
        else:
            return ""

    def parse_date(self, date_str):
        from datetime import datetime
        return datetime.strptime(date_str, "%d/%m/%Y")

    def add_notification(self, layout, entity, status, due_date):
        notification_frame = QFrame()
        notification_frame.setFixedHeight(80)  # Consistent height for each notification bar
        notification_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        notification_layout = QHBoxLayout(notification_frame)
        notification_layout.setContentsMargins(10, 10, 10, 10)
        notification_layout.setSpacing(10)

        # Vertical layout for entity name and description
        details_layout = QVBoxLayout()
        details_layout.setContentsMargins(0, 0, 0, 0)

        # Entity Name
        entity_label = QLabel(f"{entity}")
        entity_label.setStyleSheet("font-weight: bold; font-size: 15px;")
        details_layout.addWidget(entity_label)
        
        # Description (status)
        status_label = QLabel(f"{status}")
        details_layout.addWidget(status_label)

        # Spacer for separation between description and dates
        details_layout.addSpacerItem(QSpacerItem(5, 5, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Due date and current time
        datetime_label = QLabel(f"due date: {due_date}")
        datetime_label.setStyleSheet("font-size: 12px;")
        details_layout.addWidget(datetime_label)

        notification_layout.addLayout(details_layout)

        # Close button with left border
        close_button = QPushButton("X")
        close_button.setFixedSize(50, 70)

        close_button.clicked.connect(lambda: self.remove_notification(layout, notification_frame))
        
        # Add the close button to the right side
        notification_layout.addWidget(close_button, alignment=Qt.AlignRight | Qt.AlignTop)

        # Add the frame to the layout
        layout.insertWidget(0, notification_frame)  # Insert at the top

    def remove_notification(self, layout, frame):
        # Remove the notification frame from the layout
        layout.removeWidget(frame)
        frame.deleteLater()

    def show_return_page(self):
        # Set the stacked widget to display the return page
        self.main_window.stacked_widget.setCurrentWidget(self.main_window.borrowreturnload_page)
        self.main_window.borrowreturnload_page.loadborrowreturnpage('Return')

    def show_borrow_page(self):
        # Set the stacked widget to display the borrow page
        self.main_window.stacked_widget.setCurrentWidget(self.main_window.borrowreturnload_page)
        self.main_window.borrowreturnload_page.loadborrowreturnpage('Borrow')