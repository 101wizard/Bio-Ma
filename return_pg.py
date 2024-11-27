import sys
from PySide6.QtWidgets import  QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QScrollArea,QFrame, QSpacerItem, QSizePolicy, QLineEdit, QMessageBox, QComboBox,QGridLayout
from PySide6.QtCore import Qt, QByteArray, QRect
from PySide6.QtGui import QImage, QPixmap, QPainter, QIntValidator
import qtawesome as qta 
import base64
import mysql.connector
import numpy as np
import datetime

class ReturnPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.user_id = None  # To store the recognized researcher ID
        self.selected_amounts = {}

        # Main layout
        self.setLayout(QVBoxLayout(self))

        # Label
        label = QLabel('Return')
        label.setStyleSheet("font-family: 'Times [Adobe]'; color: #ffffff; padding: 15px; font-size: 20px; font-weight: bold;")
        self.layout().addWidget(label)

        # Layout for search bar and scroll area
        content_layout = QVBoxLayout()

        # Dropbox layout
        dropbox_layout = QHBoxLayout()

        # Dropbox
        self.borrow_id_dropdown = QComboBox()
        self.borrow_id_dropdown.setStyleSheet("font-size: 15px;")
        self.borrow_id_dropdown.addItem("Select borrow ID...")  # Placeholder
        self.borrow_id_dropdown.currentIndexChanged.connect(self.load_borrowed_equipment)  # Load equipment on change
        dropbox_layout.addWidget(self.borrow_id_dropdown)

        content_layout.addLayout(dropbox_layout)

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
        self.confirm_button = QPushButton("Return")
        self.confirm_button.setFixedSize(100, 40)
        self.confirm_button.setStyleSheet("background-color: #ffffff; color:#000000; font-size: 16px; padding: 10px; border-radius: 5px;")
        self.confirm_button.clicked.connect(self.confirm_selection)

        # Set the position of the button
        self.confirm_button.setGeometry(QRect(self.width() - 120, self.height() - 60, 100, 40))  # Position at bottom right

        # Add the confirm button to the main widget
        self.layout().addWidget(self.confirm_button)

        # Ensure the equipment_content adjusts properly
        self.equipment_content.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

    def loadreturnpage(self, id):
        self.user_id = id
        self.selected_amounts.clear()
        self.all_equipment = self.fetch_equipment_list()
        self.borrow_list = self.fetch_borrow_list()
        self.populate_borrow_id_dropdown()
        self.clear_list()
        
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

    def fetch_borrow_list(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="test"
            )
            cursor = connection.cursor()

            # SQL Query to fetch borrow_id from the borrow table using the r_id
            borrow_query = f"SELECT borrow_id FROM borrow WHERE r_id = {self.user_id};"
            cursor.execute(borrow_query)

            # Fetch all the borrow IDs
            borrow_data = cursor.fetchall()

            # Prepare the final borrow list
            borrow_list = []

            # Iterate over each borrow_id
            for row in borrow_data:
                borrow_id = row[0]

                # Query to fetch e_id and amount from borrowed_equipment table for this borrow_id
                equipment_query = f"SELECT e_id, amount FROM borrowed_equipment WHERE borrow_id = {borrow_id};"
                cursor.execute(equipment_query)

                # Fetch the equipment details
                equipment_data = cursor.fetchall()

                # Prepare the list of (e_id, amount) tuples
                equipment_list = [(e_id, amount) for e_id, amount in equipment_data]

                # Append the tuple (borrow_id, equipment_list) to borrow_list
                borrow_list.append((borrow_id, tuple(equipment_list)))

            # Return the formatted borrow list
            return borrow_list

        except mysql.connector.Error as e:
            # Handle any SQL or connection errors
            print(f"An error occurred while fetching the borrow list: {e}")
            return []

        finally:
            # Ensure the connection is closed properly
            if connection:
                connection.close()

    def populate_borrow_id_dropdown(self):
        # Clear existing items first (except for the placeholder)
        self.borrow_id_dropdown.clear()
        self.borrow_id_dropdown.addItem("Select borrow ID...")  # Placeholder

        # Add formatted borrow_ids from self.borrow_list
        for borrow_id, _ in self.borrow_list:
            formatted_borrow_id = f"B{borrow_id:04d}"
            self.borrow_id_dropdown.addItem(formatted_borrow_id)

        # Reset the dropdown index to the placeholder
        self.borrow_id_dropdown.setCurrentIndex(0)

    def populate_equipment_list(self, equipment_list):
        self.clear_list()

        # Add equipment items to layout
        for img, name, amount, equipment_id in equipment_list:
            self.add_equipment_item(img, name, amount, equipment_id)

    def clear_list(self):
        # Clear existing equipment items
        while self.equipment_layout.count() > 0: 
            item = self.equipment_layout.takeAt(0)  # Take the first item
            if item.widget():  # If the item is a widget
                item.widget().deleteLater()  # Delete the widget

        self.selected_amounts = {}

    def add_equipment_item(self, img, name, borrowed_amount, equipment_id):
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
        details_layout = QGridLayout()
        details_layout.setContentsMargins(0, 0, 0, 0)

        # Name and In-Stock
        name_label = QLabel("Name:")
        name_det = QLabel(name)
        id_label = QLabel("Equipment ID:")
        id_det = QLabel(equipment_id)
        amount_label = QLabel("Amount Borrowed:")
        amount_det = QLabel(str(borrowed_amount))

        details_layout.addWidget(name_label,0,0)
        details_layout.addWidget(name_det,0,1)
        details_layout.addWidget(id_label,1,0)
        details_layout.addWidget(id_det,1,1)
        details_layout.addWidget(amount_label,2,0)
        details_layout.addWidget(amount_det,2,1)

        # Number Picker for return selection and missing field
        return_label = QLabel("Return Amount:")
        missing_label = QLabel("Missing Amount:")

        num_layout = QHBoxLayout()
        amount_field = QLineEdit("0")
        amount_field.setValidator(QIntValidator())
        amount_field.setFixedSize(50, 30)
        amount_field.setAlignment(Qt.AlignmentFlag.AlignCenter)
        amount_field.setStyleSheet("background-color: #484848; color: #ffffff; border-radius: 5px;")

        missing_field = QLineEdit(str(borrowed_amount))
        missing_field.setValidator(QIntValidator())
        missing_field.setFixedSize(50, 30)
        missing_field.setAlignment(Qt.AlignmentFlag.AlignCenter)
        missing_field.setStyleSheet("background-color: #484848; color: #ffffff; border-radius: 5px;")
        missing_field.setDisabled(True)

        amount_field.textChanged.connect(lambda: self.validate_amount_field(amount_field, borrowed_amount, missing_field))

        minus_button = QPushButton("-")
        minus_button.setFixedSize(30, 30)
        minus_button.setStyleSheet("background-color: #484848; color: #ffffff;")
        minus_button.clicked.connect(lambda: self.decrease_total(amount_field))

        plus_button = QPushButton("+")
        plus_button.setFixedSize(30, 30)
        plus_button.setStyleSheet("background-color: #484848; color: #ffffff;")
        plus_button.clicked.connect(lambda: self.increase_total(amount_field, borrowed_amount))

        num_layout.addWidget(minus_button)
        num_layout.addWidget(amount_field)
        num_layout.addWidget(plus_button)

        details_layout.addWidget(return_label,3,0)
        details_layout.addLayout(num_layout,3,1)
        details_layout.addWidget(missing_label,4,0)
        details_layout.addWidget(missing_field,4,1)     

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

        self.selected_amounts[equipment_id] = (amount_field, missing_field)

    def decrease_total(self, amount_field):
        current_value = int(amount_field.text())
        if current_value > 0:
            amount_field.setText(str(current_value - 1))

    def increase_total(self, amount_field, max_amount):
        current_value = int(amount_field.text())
        if current_value < max_amount:
            amount_field.setText(str(current_value + 1))

    def validate_amount_field(self, amount_field, max_amount, missing_field):
        current_value = int(amount_field.text()) if amount_field.text() else 0
        
        # Enforce upper restraint
        if current_value > max_amount:
            amount_field.setText(str(max_amount))
            current_value = max_amount

        amount = max_amount - current_value
        missing_field.setText(str(amount))

    def confirm_selection(self):
        current_index = self.borrow_id_dropdown.currentIndex()
        if current_index > 0:
            borrow_id = self.borrow_list[current_index - 1][0]

            formatted_borrow_id = f"B{borrow_id:04d}"
            print(f"Selected Borrow ID: {formatted_borrow_id}")
            return_list = []
        
            for equipment_id, (return_amount_field, missing_amount_field) in self.selected_amounts.items():
                return_amount = int(return_amount_field.text())
                missing_amount = int(missing_amount_field.text())
                
                return_list.append((equipment_id, return_amount, missing_amount))
            
            # Now return_list contains tuples of (equipment_id, return_amount, missing_amount)
            print(return_list)

            # Create a formatted string of selected items for the message box
            item_list = "\n".join([f"Equipment ID: {equipment_id}, Amount: {return_amount}, Missing: {missing_amount}" for equipment_id, return_amount, missing_amount in return_list])
            message = f"The following items will be returned:\n{item_list}\n\nDo you want to proceed?"

                # Show the confirmation dialog
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Confirm Return")
            msg_box.setText(message)
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

            # Change button text for "Yes" and "No"
            msg_box.button(QMessageBox.Yes).setText("Confirm")
            msg_box.button(QMessageBox.No).setText("Cancel")

            reply = msg_box.exec_()

            if reply == QMessageBox.No:  # User clicked "Cancel"
                self.main_window.show_dashboard()
                print("Return operation canceled by the user.")
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

                # Step 2: Remove into the 'borrow' table
                delete_borrowed_equipment_query = "DELETE FROM borrowed_equipment WHERE borrow_id = %s"
                cursor.execute(delete_borrowed_equipment_query, (borrow_id,))
                connection.commit()  

                delete_borrow_query = "DELETE FROM borrow WHERE borrow_id = %s"
                cursor.execute(delete_borrow_query, (borrow_id,))
                connection.commit()
                
                # Prepare the SQL query using CASE to handle multiple equipment updates
                equipment_ids = [int(equipment_id[1:]) for equipment_id, _, _ in return_list]
                update_equipment_query = """
                    UPDATE equipment
                    SET
                        e_amount = e_amount - CASE e_id
                            {e_amount_cases}
                            ELSE e_amount END,
                        e_curr_amount = e_curr_amount + CASE e_id
                            {e_curr_amount_cases}
                            ELSE e_curr_amount END
                    WHERE e_id IN ({equipment_ids})
                """

                # Generate the CASE statements for e_amount and e_curr_amount
                e_amount_cases = "\n".join(
                    [f"WHEN {int(equipment_id[1:])} THEN {int(missing_amount)}" for equipment_id, _, missing_amount in return_list]
                )

                e_curr_amount_cases = "\n".join(
                    [f"WHEN {int(equipment_id[1:])} THEN {int(return_amount)}" for equipment_id, return_amount, _ in return_list]
                )

                # Format the query with the generated CASE statements and equipment_ids
                formatted_query = update_equipment_query.format(
                    e_amount_cases=e_amount_cases,
                    e_curr_amount_cases=e_curr_amount_cases,
                    equipment_ids=", ".join(map(str, equipment_ids))
                )

                # Execute the formatted query
                cursor.execute(formatted_query)
                connection.commit()

                print("Transaction successful, database updated.")

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

        print("default no selection")

    def get_default_image(self):
        # Create a default image using a Qt Awesome icon
        icon = qta.icon('fa.file-image-o', color='white')  # Use Qt Awesome icon
        pixmap = QPixmap(180, 180)
        pixmap.fill(Qt.transparent)  # Fill with transparent background
        painter = QPainter(pixmap)
        icon.paint(painter, pixmap.rect())
        painter.end()
        return pixmap
    
    def load_borrowed_equipment(self):
        # Get the current selected index
        current_index = self.borrow_id_dropdown.currentIndex()
        self.selected_amounts.clear()

        # Ignore the placeholder selection (index 0)
        if current_index > 0:
            # Get the corresponding borrow_id from self.borrow_list
            borrow_id = self.borrow_list[current_index - 1][0]  # Adjust for the placeholder

            # Print the selected borrow_id in the desired format
            formatted_borrow_id = f"B{borrow_id:04d}"
            print(f"Selected Borrow ID: {formatted_borrow_id}")

            # Get the borrowed equipment for the selected borrow_id
            borrowed_equipment = self.borrow_list[current_index - 1][1]  # (e_id, amount) pairs

            # Filter the full equipment list (self.all_equipment) based on borrowed equipment
            matched_equipment_list = []
            for e_id, borrowed_amount in borrowed_equipment:
                for equipment in self.all_equipment:
                    if equipment[4] == e_id:  # Match e_id in self.all_equipment
                        img, name, _, _, _ = equipment  # Unpack equipment details
                        equipment_id = f"E{e_id:04d}"  # Format equipment ID
                        matched_equipment_list.append((img, name, borrowed_amount, equipment_id))

            # Populate the equipment list with the matched equipment
            self.populate_equipment_list(matched_equipment_list)

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
