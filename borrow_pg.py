import sys
from PySide6.QtWidgets import  QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QScrollArea,QFrame, QSpacerItem, QSizePolicy, QLineEdit, QMessageBox
from PySide6.QtCore import Qt, QByteArray, QRect
from PySide6.QtGui import QImage, QPixmap, QPainter, QIntValidator
import qtawesome as qta 
import base64
import mysql.connector
import numpy as np
import datetime

class BorrowPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.user_id = None  # To store the recognized researcher ID
        self.selected_amounts = {}  # Track the selected amounts

        # Main layout
        self.setLayout(QVBoxLayout(self))

        # Label
        label = QLabel('Borrow')
        label.setStyleSheet("font-family: 'Times [Adobe]'; color: #ffffff; padding: 15px; font-size: 20px; font-weight: bold;")
        self.layout().addWidget(label)

        # Layout for search bar and scroll area
        content_layout = QVBoxLayout()

        # Search bar layout
        search_layout = QHBoxLayout()

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search equipment...")
        self.search_bar.setStyleSheet("font-size: 15px;")
        self.search_bar.textChanged.connect(self.filter_equipment)  # Connect to search function
        search_layout.addWidget(self.search_bar)

        content_layout.addLayout(search_layout)

        # Scrollable area for equipment list
        self.equipment_content = QWidget()
        self.equipment_layout = QVBoxLayout(self.equipment_content)
        self.equipment_layout.setContentsMargins(0, 0, 0, 0)
        self.equipment_layout.setSpacing(20)
        self.equipment_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Top border for scroll area
        top_border = QWidget()
        top_border.setFixedHeight(1)
        top_border.setStyleSheet("background-color: #ffffff;")
        content_layout.addWidget(top_border)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Hide the vertical scrollbar
        scroll_area.setWidget(self.equipment_content)
        content_layout.addWidget(scroll_area)

        # Bottom border for scroll area
        bottom_border = QWidget()
        bottom_border.setFixedHeight(1)
        bottom_border.setStyleSheet("background-color: #ffffff;")
        content_layout.addWidget(bottom_border)

        # Style the content layout
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        content_widget.setStyleSheet("""QWidget {
                                            background-color: #303030; 
                                            border-radius: 10px;
                                            color: #ffffff;
                                            font-size: 15px;
                                        }""")
        self.layout().addWidget(content_widget)

        # Confirm button
        self.confirm_button = QPushButton("Borrow")
        self.confirm_button.setFixedSize(100, 40)
        self.confirm_button.setStyleSheet("background-color: #ffffff; color:#000000; font-size: 16px; padding: 10px; border-radius: 5px;")
        self.confirm_button.clicked.connect(self.confirm_selection)

        # Set the position of the button
        self.confirm_button.setGeometry(QRect(self.width() - 120, self.height() - 60, 100, 40))  # Position at bottom right

        # Add the confirm button to the main widget
        self.layout().addWidget(self.confirm_button)

        # Ensure the equipment_content adjusts properly
        self.equipment_content.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

    def loadborrowpage(self, id):
        self.selected_amounts.clear()  # Clear previous selections
        self.all_equipment = self.fetch_equipment_list()
        self.populate_equipment_list(self.all_equipment)
        self.user_id = id

    def fetch_equipment_list(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="test"
            )
            cursor = connection.cursor()

            # SQL Query to fetch equipment details including the image (e_img)
            query = "SELECT e_id, e_name, e_curr_amount, e_amount, e_img FROM equipment"
            cursor.execute(query)

            # Fetch all the results
            equipment_data = cursor.fetchall()

            # Prepare the equipment list in the desired format
            equipment_list = []
            for row in equipment_data:
                equipment_list.append((row[4], row[1], row[2], row[3], row[0]))

            # Return the formatted equipment list
            return equipment_list

        except mysql.connector.Error as e:
            # Handle any SQL or connection errors
            print(f"An error occurred while fetching the equipment list: {e}")
            return []

        finally:
            # Ensure the connection is closed properly
            if connection:
                connection.close()

    def save_selected_amounts(self):
        # Save the current values from the QLineEdit fields into the selected_amounts dictionary
        for eid, field in self.selected_amounts.items():
            self.selected_amounts[eid] = field.text() if isinstance(field, QLineEdit) else field

    def populate_equipment_list(self, equipment_list):
        # Clear existing equipment items
        while self.equipment_layout.count() > 0: 
            item = self.equipment_layout.takeAt(0)  # Take the first item
            if item.widget():  # If the item is a widget
                item.widget().deleteLater()  # Delete the widget

        # Add equipment items to layout
        for img, name, current_amount, amount, id in equipment_list:
            equipment_id = f"E{id:04d}"  # Format ID
            self.add_equipment_item(img, name, current_amount, amount, equipment_id)

    def add_equipment_item(self, img, name, current_amount, amount, equipment_id):
        equipment_frame = QFrame()
        equipment_frame.setFixedHeight(200)  # Consistent height for each equipment bar
        layout = QVBoxLayout(equipment_frame)
        equipment_layout = QHBoxLayout()
        equipment_layout.setContentsMargins(10, 0, 10, 0)
        equipment_layout.setSpacing(10)

        # Equipment image
        equipment_image = QLabel()
        equipment_image.setFixedSize(180, 180)
        equipment_image.setStyleSheet("""border:1px solid #ffffff""")
        equipment_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        equipment_layout.addWidget(equipment_image)

        if img != '':
            image_data = QByteArray.fromBase64(img)
            pixmap = QPixmap(QImage.fromData(image_data))
            self.set_rounded_pixmap(equipment_image, pixmap)
        else:
            pixmap = self.get_default_image()
            equipment_image.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))  # Scale image

        # Equipment details layout
        details_layout = QVBoxLayout()
        details_layout.setContentsMargins(0, 0, 0, 0)

        # Name and In-Stock
        name_label = QLabel(f"Name:     {name}")
        stock_label = QLabel(f"In-Stock: {current_amount}/{amount}")
        details_layout.addWidget(name_label)
        details_layout.addWidget(stock_label)

        # Spacer to separate from Equipment ID
        details_layout.addSpacerItem(QSpacerItem(0, 5, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Equipment ID
        id_label = QLabel(f"Equipment ID: {equipment_id}")
        details_layout.addWidget(id_label)

        # Number Picker for total selection
        num_layout = QHBoxLayout()
        amount_field = QLineEdit("0")
        amount_field.setValidator(QIntValidator())
        amount_field.setFixedSize(50, 30)
        amount_field.setAlignment(Qt.AlignmentFlag.AlignCenter)
        amount_field.setStyleSheet("background-color: #484848; color: #ffffff; border-radius: 5px;")

        amount_field.textChanged.connect(lambda: self.validate_amount_field(amount_field, current_amount))

        if equipment_id in self.selected_amounts:
            value = self.selected_amounts[equipment_id]
            if isinstance(value, QLineEdit):  # Ensure value is a string
                amount_field.setText(value.text())
            else:
                amount_field.setText(str(value))

        minus_button = QPushButton("-")
        minus_button.setFixedSize(30, 30)
        minus_button.setStyleSheet("background-color: #484848; color: #ffffff;")
        minus_button.clicked.connect(lambda: self.decrease_total(amount_field))

        plus_button = QPushButton("+")
        plus_button.setFixedSize(30, 30)
        plus_button.setStyleSheet("background-color: #484848; color: #ffffff;")
        plus_button.clicked.connect(lambda: self.increase_total(amount_field, current_amount))

        num_layout.addWidget(minus_button)
        num_layout.addWidget(amount_field)
        num_layout.addWidget(plus_button)

        details_layout.addLayout(num_layout)

        equipment_layout.addLayout(details_layout)
        layout.addLayout(equipment_layout)

        # Add the frame to the layout
        self.equipment_layout.addWidget(equipment_frame)

        # Separator line
        line = QFrame()
        line.setLineWidth(1)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Plain)
        line.setStyleSheet("background-color: #ffffff;")
        line.setFixedHeight(1)

        self.equipment_layout.addWidget(line)

        # Store reference to amount field
        self.selected_amounts[equipment_id] = amount_field

    def decrease_total(self, amount_field):
        current_value = int(amount_field.text())
        if current_value > 0:
            amount_field.setText(str(current_value - 1))

    def increase_total(self, amount_field, max_amount):
        current_value = int(amount_field.text())
        if current_value < max_amount:
            amount_field.setText(str(current_value + 1))

    def validate_amount_field(self, amount_field, max_amount):
        current_value = int(amount_field.text()) if amount_field.text() else 0
        
        # Enforce upper restraint
        if current_value > max_amount:
            amount_field.setText(str(max_amount))

    def confirm_selection(self):
        # Filter selected items (amount > 0)
        selected_items = {
            eid: field.text() if isinstance(field, QLineEdit) else field
            for eid, field in self.selected_amounts.items()
            if (isinstance(field, QLineEdit) and int(field.text()) > 0) or (isinstance(field, str) and field.isdigit() and int(field) > 0)
        }

        if not selected_items:
            wrn_box = QMessageBox(self)
            wrn_box.setWindowTitle("No Equipment Selected")
            wrn_box.setText("No equipment selected to borrow.")
            wrn_box.setStandardButtons(QMessageBox.Yes)

            wrn_box.button(QMessageBox.Yes).setText("OK")
            wrn_box.exec_()
            return
        
        # Create a formatted string of selected items for the message box
        item_list = "\n".join([f"Equipment ID: {eid}, Amount: {amount}" for eid, amount in selected_items.items()])
        message = f"The following items will be borrowed:\n{item_list}\n\nDo you want to proceed?"

            # Show the confirmation dialog
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Borrow")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # Change button text for "Yes" and "No"
        msg_box.button(QMessageBox.Yes).setText("Confirm")
        msg_box.button(QMessageBox.No).setText("Cancel")

        reply = msg_box.exec_()

        if reply == QMessageBox.No:  # User clicked "Cancel"
            self.main_window.show_dashboard()
            print("Borrow operation canceled by the user.")
            return  # Skip the operation if the user clicked "Cancel"
            
        try:
            # Step 1: Connect to the database
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="test"
            )
            cursor = connection.cursor()

            # Step 2: Insert into the 'borrow' table
            r_id = self.user_id  # Researcher ID
            la_id = int(self.main_window.uid[2:])  # Lab assistant ID
            borrow_date = datetime.datetime.now()
            due_date = borrow_date + datetime.timedelta(days=7)

            # Prepare the query for the 'borrow' table
            query = """
                INSERT INTO borrow (r_id, la_id, borrow_date, due_date)
                VALUES (%s, %s, %s, %s)
            """
            values = (r_id, la_id, borrow_date, due_date)
            
            # Execute the query
            cursor.execute(query, values)
            connection.commit()  # Commit the transaction to the database

            # Get the auto-incremented borrow_id
            borrow_id = cursor.lastrowid
            if not borrow_id:
                print("Failed to retrieve borrow ID after insertion.")
                return

            print(f"New borrow record created with borrow_id: {borrow_id}")

            # Step 3: Insert into the 'borrowed_equipment' table
            for eid, amount in selected_items.items():
                # Prepare the query for the 'borrowed_equipment' table
                query = """
                    INSERT INTO borrowed_equipment (borrow_id, e_id, amount)
                    VALUES (%s, %s, %s)
                """
                values = (borrow_id, int(eid[1:]), int(amount))  # Ensure amount is stored as an integer
                
                # Execute the query
                cursor.execute(query, values)
                connection.commit() 

                print(f"Equipment {eid} with amount {amount} added to 'borrowed_equipment'.")

                # Step 4: Update the equipment count in the 'equipment' table (reduce e_curr_amount)
                update_query = """
                    UPDATE equipment 
                    SET e_curr_amount = e_curr_amount - %s
                    WHERE e_id = %s
                """
                update_values = (int(amount), int(eid[1:]))

                cursor.execute(update_query, update_values)
                connection.commit() 

                print("Borrow transaction completed successfully.")

        except mysql.connector.Error as e:
            # Handle database errors
            QMessageBox.warning(self, "Database Error", f"An error occurred while processing the transaction: {e}")
            print(f"Error: {e}")
            return

        finally:
            # Ensure the connection is closed properly
            if connection.is_connected():
                cursor.close()
                connection.close()

        self.main_window.show_dashboard()

    def get_default_image(self):
        # Create a default image using a Qt Awesome icon
        icon = qta.icon('fa.file-image-o', color='white')  # Use Qt Awesome icon
        pixmap = QPixmap(180, 180)
        pixmap.fill(Qt.transparent)  # Fill with transparent background
        painter = QPainter(pixmap)
        icon.paint(painter, pixmap.rect())
        painter.end()
        return pixmap
    
    def filter_equipment(self):
        search_text = self.search_bar.text().lower()
        
        # Save the current selected amounts before filtering
        self.save_selected_amounts()
        
        # Filter the equipment list based on the current search text
        filtered_equipment = (
            [item for item in self.all_equipment if search_text in item[1].lower()]
            if search_text  # If there is text in the search bar
            else self.all_equipment  # If search bar is empty, show all equipment
        )
        
        # Populate the filtered equipment list
        self.populate_equipment_list(filtered_equipment)

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