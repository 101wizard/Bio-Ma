from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea,
    QFrame, QSpacerItem, QSizePolicy, QLineEdit, QGridLayout, QFileDialog
)
from PySide6.QtCore import Qt, QByteArray, QSize
from PySide6.QtGui import QPixmap, QPainter, QImage
import qtawesome as qta 
import mysql.connector

class UserFrameTemplate(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        # Main layout
        main_layout = QVBoxLayout(self)

        # Title Label
        self.title_label = QLabel()
        self.title_label.setStyleSheet("""font-family: "Times [Adobe]";
                                          color: #ffffff;
                                          padding: 15px;
                                          font-size: 20px;
                                          font-weight: bold;""")

        # Widget content area
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Spacer item
        spacer = QWidget()
        spacer.setFixedWidth(20)

        # Details layout with QGridLayout
        details_layout = QGridLayout()

        # User image
        self.user_image = QLabel()
        self.user_image.setFixedSize(300, 300)
        self.user_image.setStyleSheet("border: 1px solid #ffffff;")
        self.user_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add Image Button (inside the image)
        self.image_button = QPushButton(qta.icon('ri.image-add-fill', color='black'), "")
        self.image_button.setIconSize(QSize(24, 24))
        self.image_button.setFixedSize(30, 30)
        self.image_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border-radius: 15px;
                color: #000000;
            }
            QPushButton:hover {
                background-color: #383838;
            }
        """)
        self.image_button.clicked.connect(self.select_image)

        # Stack the image and button using a layout
        image_layout = QVBoxLayout(self.user_image)
        image_layout.addWidget(self.image_button, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        # User image (placed in the first row, first column)
        details_layout.addWidget(self.user_image, 0, 0, 4, 1, Qt.AlignmentFlag.AlignLeft)  # Spanning 3 rows for the image

        # Spacer item
        spacer = QWidget()
        spacer.setFixedWidth(20)
        details_layout.addWidget(spacer, 0, 1, 4, 1)  # Spanning 4 rows for the spacer

        # Details label layout in the grid
        name_label = QLabel("Name:")
        id_label = QLabel("User ID:")
        phone_label = QLabel("Phone:")
        email_label = QLabel("Email:")

        # Add labels to the grid
        details_layout.addWidget(name_label, 0, 1, Qt.AlignmentFlag.AlignVCenter)
        details_layout.addWidget(id_label, 1, 1, Qt.AlignmentFlag.AlignVCenter)
        details_layout.addWidget(phone_label, 2, 1, Qt.AlignmentFlag.AlignVCenter)
        details_layout.addWidget(email_label, 3, 1, Qt.AlignmentFlag.AlignVCenter)

        # Details content layout in the grid
        self.u_vname = QLabel()
        self.user_name = QLineEdit()
        self.user_name.setStyleSheet("background-color: #484848; color: #ffffff;")
        self.u_vid = QLabel()
        self.u_vphone = QLabel()
        self.user_phone = QLineEdit()
        self.user_phone.setStyleSheet("background-color: #484848; color: #ffffff;")
        self.u_vemail = QLabel()
        self.user_email = QLineEdit()
        self.user_email.setStyleSheet("background-color: #484848; color: #ffffff;")

        # Add content to the grid next to the labels
        details_layout.addWidget(self.u_vname, 0, 2, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        details_layout.addWidget(self.u_vid, 1, 2, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        details_layout.addWidget(self.u_vphone, 2, 2, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        details_layout.addWidget(self.u_vemail, 3, 2, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        layout.addLayout(details_layout)

        # Edit Remove Save button section layout
        button_section = QHBoxLayout()
        button_section.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Edit Remove Save button
        self.e_vedit = QPushButton("Edit")
        self.e_vedit.setStyleSheet("font-size: 15px; color: #000000; background-color: #ffffff; border-radius: 10px;")
        self.e_vedit.setFixedSize(80, 25)
        self.e_vremove = QPushButton("Remove")
        self.e_vremove.setStyleSheet("font-size: 15px; color: #000000; background-color: #ffffff; border-radius: 10px;")
        self.e_vremove.setFixedSize(80, 25)
        self.e_vsave = QPushButton("Save")
        self.e_vsave.setStyleSheet("font-size: 15px; color: #000000; background-color: #ffffff; border-radius: 10px;")
        self.e_vsave.setFixedSize(80, 25)
        self.e_vcancel = QPushButton("Cancel")
        self.e_vcancel.setStyleSheet("font-size: 15px; color: #000000; background-color: #ffffff; border-radius: 10px;")
        self.e_vcancel.setFixedSize(80, 25)

        self.e_vedit.clicked.connect(lambda: self.edit())
        self.e_vremove.clicked.connect(lambda: self.remove())
        self.e_vsave.clicked.connect(lambda: self.save(self.u_vid.text(), self.title_label.text()))
        self.e_vcancel.clicked.connect(lambda: self.cancel(self.u_vid.text(), self.title_label.text()))

        button_section.addWidget(self.e_vedit)
        button_section.addWidget(self.e_vremove)
        button_section.addWidget(self.e_vsave)
        button_section.addWidget(self.e_vcancel)

        layout.addLayout(button_section)

        # Top border for list section
        top_border = QWidget()
        top_border.setFixedHeight(1)
        top_border.setStyleSheet("background-color: #ffffff;")
        layout.addWidget(top_border)

        # Label for column headers
        header_frame = QFrame()
        header_frame.setFixedHeight(50)  # Set a fixed height similar to content items
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 0, 20, 0)  # Match margins with content layout
        header_layout.setSpacing(10)  # Match spacing with content layout

        # Borrow-ID header
        borrow_header = QLabel("Borrow ID")
        header_layout.addWidget(borrow_header)

        # User-ID header
        self.user_header = QLabel()
        header_layout.addWidget(self.user_header)

        # Date header
        date_header = QLabel("Return Date")
        header_layout.addWidget(date_header)

        # Detail header
        detail_header = QLabel("Details")
        header_layout.addWidget(detail_header, alignment=Qt.AlignRight)
        
        layout.addWidget(header_frame)

        # Scrollable area for list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Hide the vertical scrollbar
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable horizontal scrolling

        self.borrow_content = QWidget()
        self.borrow_layout = QVBoxLayout(self.borrow_content)
        self.borrow_layout.setContentsMargins(0, 0, 0, 0)
        self.borrow_layout.setSpacing(20)
        self.borrow_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area.setWidget(self.borrow_content)

        layout.addWidget(scroll_area)
        
        widget.setLayout(layout)
        widget.setStyleSheet("""QWidget {
                                        background-color: #303030; 
                                        border-radius: 10px;
                                        color: #ffffff;
                                        font-size: 15px;
                                      }""")

        # Add widgets to layout
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Adjust the size of the equipment_content to fit its contents without expanding
        self.borrow_content.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum) 

        self.content_layout = layout

    def fetch_borrow_list(self, user_id, entity):
        # If entity is lab assistant or researcher or profile based on entity
        try:
            # Step 1: Format user_id based on the entity
            if entity == 'Profile':
                formatted_user_id = int(user_id[2:])  # Convert LA0001 -> 1
                query = """
                    SELECT borrow_id, r_id, due_date
                    FROM borrow
                    WHERE la_id = %s
                """
            elif entity == 'User : Lab Assistant':
                formatted_user_id = int(user_id[2:])  # Convert LA0001 -> 1
                query = """
                    SELECT borrow_id, r_id, due_date
                    FROM borrow
                    WHERE la_id = %s
                """
            elif entity == 'User : Researcher':
                formatted_user_id = int(user_id[1:])  # Convert R0001 -> 1
                query = """
                    SELECT borrow_id, la_id, due_date
                    FROM borrow
                    WHERE r_id = %s
                """
            else:
                print("Invalid entity type.")
                return []

            # Step 2: Connect to the database
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="test"
            )
            cursor = connection.cursor()

            # Step 3: Execute the query and fetch data
            cursor.execute(query, (formatted_user_id,))
            borrow_list = cursor.fetchall()

            # Step 4: Return the borrow list (format: borrow_id, r_id/la_id, due_date)
            return borrow_list

        except mysql.connector.Error as e:
            print(f"Error fetching borrow list: {e}")
            return []
        
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def populate_borrow_list(self, borrow_list, title):
        # Clear existing equipment items
        while self.borrow_layout.count() > 0: 
            item = self.borrow_layout.takeAt(0)  # Take the first item
            if item.widget():  # If the item is a widget
                item.widget().deleteLater()  # Delete the widget

        # Add equipment items to layout
        for bid, uid, due_date in borrow_list:
            borrow_id = f"B{bid:04d}"  # Format ID
            if title == "User : Lab Assistant":
                user_id   = f"R{uid:04d}"  # Format ID
            else:
                user_id   = f"LA{uid:04d}"  # Format ID
            self.add_borrow(borrow_id, user_id, due_date)

    def add_borrow(self, borrow_id, user_id, due_date):
        item_frame = QFrame()
        item_frame.setFixedHeight(40)  # Consistent height for each item
        layout = QVBoxLayout(item_frame)
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(10, 0, 10, 0)
        item_layout.setSpacing(10)

        # Borrow-ID 
        borrow_label = QLabel(borrow_id)
        item_layout.addWidget(borrow_label)

        # User-ID 
        user_label = QLabel(user_id)
        item_layout.addWidget(user_label)

        # Date 
        date_label = QLabel(str(due_date))
        item_layout.addWidget(date_label)

        # View button
        view_button = QPushButton("View")
        view_button.setStyleSheet("text-decoration: underline;")
        view_button.setFixedSize(50, 20)
        view_button.clicked.connect(lambda: self.view_borrow_page(borrow_id))
        
        # Add the button to the right side
        item_layout.addWidget(view_button, alignment=Qt.AlignRight | Qt.AlignTop)

        layout.addLayout(item_layout)

        # Add the frame to the layout
        self.borrow_layout.addWidget(item_frame)

    def view_borrow_page(self, bid):
        self.main_window.borrow_details.update_content(borrow_id=bid)
        self.main_window.stacked_widget.setCurrentWidget(self.main_window.borrow_details)
        print(f"Viewing Borrow ID: {bid}")

    def save(self, user_id, title):
        self.update_content(user_id, title)
        if title == "Profile":
            self.e_vremove.hide()
        else:
            self.e_vremove.show()
        self.e_vedit.show()
        self.e_vsave.hide()
        self.e_vcancel.hide()
        print("save")

    def edit(self):
        self.e_vedit.hide()
        self.e_vremove.hide()
        self.e_vsave.show()
        self.e_vcancel.show()
        print("edit")

    def cancel(self, user_id, title):
        if title == "Profile":
            self.e_vremove.hide()
        else:
            self.e_vremove.show()
        self.e_vedit.show()
        self.e_vsave.hide()
        self.e_vcancel.hide()
        print("cancel")

    def remove(self):
        self.main_window.stacked_widget.setCurrentWidget(self.main_window.user_page)
        print("remove")

    def select_image(self):
        self.aepic_path = ''
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.xpm *.jpg)")
        if file_path:
            self.aepic_path = file_path
            pixmap = QPixmap(file_path)
            self.set_rounded_pixmap(self.user_image, pixmap)

    def update_content(self, user_id, title):
        if title == "User : Lab Assistant" and user_id == self.main_window.uid:
            title = "Profile"
            self.main_window.side_nav_bar.move_indicator(self.main_window.side_nav_bar.findChild(QWidget, "Profile"))

        self.title_label.setText(title)
        content = self.fetch_content(user_id, title)

        self.user_image.setFixedSize(300, 300)
        self.user_image.setStyleSheet("""border:1px solid #ffffff""")
        self.user_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if content[4] is None or len(content[4]) == 0: 
            pixmap = self.get_default_image()
            self.user_image.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
        else:
            image_data = QByteArray.fromBase64(content[4])
            pixmap = QPixmap(QImage.fromData(image_data))
            self.set_rounded_pixmap(self.user_image, pixmap)

        self.u_vname.setText (content[1])
        self.u_vid.setText   (content[0])
        self.u_vphone.setText(content[2])
        self.u_vemail.setText(content[3])

        self.populate_borrow_list(self.fetch_borrow_list(user_id, title),title)
            
        if title == "User : Lab Assistant":
            if self.main_window.uid == "LA0001":
                self.user_header.setText("Borrower ID")
                self.e_vedit.show()
                self.e_vremove.show()
                self.e_vsave.hide()
                self.e_vcancel.hide()
            else:
                self.user_header.setText("Borrower ID")
                self.e_vedit.hide()
                self.e_vremove.hide()
                self.e_vsave.hide()
                self.e_vcancel.hide()
        elif title == "User : Researcher":
            self.user_header.setText("Approver ID")
            self.e_vsave.hide()
            self.e_vcancel.hide()
            self.e_vedit.show()
            self.e_vremove.show()
        elif title == "Profile":
            self.user_header.setText("Borrower ID")
            self.e_vsave.hide()
            self.e_vcancel.hide()
            self.e_vedit.show()
            self.e_vremove.hide()
        else:
            print('Error')

    def fetch_content(self, user_id, title):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="test"
            )
            cursor = connection.cursor()

            # Determine the query based on the title
            if title == "User : Lab Assistant":
                id_numeric_part = int(user_id[2:])
                query = "SELECT la_id, la_name, la_phone, la_email, la_img FROM lab_assistant WHERE la_id = %s"
            elif title == "User : Researcher":
                id_numeric_part = int(user_id[1:])
                query = "SELECT r_id, r_name, r_phone, r_email, r_img FROM researcher WHERE r_id = %s"
            elif title == "Profile":
                # You can decide how to fetch profile data, here assuming it's lab assistant
                id_numeric_part = int(user_id[2:])
                query = "SELECT la_id, la_name, la_phone, la_email, la_img FROM lab_assistant WHERE la_id = %s"

            # Execute the query
            cursor.execute(query, (id_numeric_part,))

            # Fetch the result
            user_data = cursor.fetchone()

            # Prepare and return the formatted result
            if user_data:
                # For Lab Assistant
                if title == "User : Lab Assistant":
                    return (f"LA{user_data[0]:04d}", user_data[1], user_data[2], user_data[3], user_data[4])
                # For Researcher
                elif title == "User : Researcher":
                    return (f"R{user_data[0]:04d}", user_data[1], user_data[2], user_data[3], user_data[4])
                # For Profile (assuming Lab Assistant)
                elif title == "Profile":
                    return (f"LA{user_data[0]:04d}", user_data[1], user_data[2], user_data[3], user_data[4])
            else:
                print("No data found for the provided user ID.")

        except mysql.connector.Error as e:
            # Handle any SQL or connection errors
            print(f"An error occurred while fetching user content: {e}")
            return []

        finally:
            # Ensure the connection is closed properly
            if connection.is_connected():
                cursor.close()
                connection.close()

    def get_default_image(self):
        # Create a default image using a Qt Awesome icon
        icon = qta.icon('fa.file-image-o', color='white')  # Use Qt Awesome icon
        pixmap = QPixmap(180, 180)
        pixmap.fill(Qt.transparent)  # Fill with transparent background
        painter = QPainter(pixmap)
        icon.paint(painter, pixmap.rect())
        painter.end()
        return pixmap

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
