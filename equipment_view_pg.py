from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QGridLayout,
    QFrame, QSpacerItem, QSizePolicy, QLineEdit, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QByteArray, QSize
from PySide6.QtGui import QPixmap, QPainter, QImage, QIntValidator
import qtawesome as qta
import base64
import mysql.connector

class EquipmentViewPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        # Main layout
        main_layout = QVBoxLayout(self)

        # Title Label
        self.title_label = QLabel('Equipment')
        self.title_label.setStyleSheet("""font-family: "Times [Adobe]";
                                          color: #ffffff;
                                          padding: 15px;
                                          font-size: 20px;
                                          font-weight: bold;""")
        
        #Picture variable
        self.aepic_path = ''
        
        # Widget content area
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Grid layout for the upper section
        grid_layout = QGridLayout()

        # Equipment image
        self.equipment_image = QLabel()
        self.equipment_image.setFixedSize(300, 300)
        self.equipment_image.setStyleSheet("border: 1px solid #ffffff;")
        self.equipment_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        image_layout = QVBoxLayout(self.equipment_image)
        image_layout.addWidget(self.image_button, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        # Add the image layout to the grid layout
        grid_layout.addWidget(self.equipment_image, 0, 0, 4, 1, Qt.AlignmentFlag.AlignLeft)  # Spanning 4 rows for the image

        # Spacer item
        spacer = QWidget()
        spacer.setFixedWidth(20)
        grid_layout.addWidget(spacer, 0, 1, 4, 1)  # Spanning 4 rows for the spacer

        # Details label layout
        name_label  = QLabel("Name:")
        id_label    = QLabel("Equipment ID:")
        stock_label = QLabel("In-Stock:")
        total_label = QLabel("Total:")

        grid_layout.addWidget(name_label, 0, 2, Qt.AlignmentFlag.AlignVCenter)
        grid_layout.addWidget(id_label, 1, 2, Qt.AlignmentFlag.AlignVCenter)
        grid_layout.addWidget(stock_label, 2, 2, Qt.AlignmentFlag.AlignVCenter)
        grid_layout.addWidget(total_label, 3, 2, Qt.AlignmentFlag.AlignVCenter)

        # Details content layout
        self.e_vname  = QLabel()
        self.equipment_name = QLineEdit()
        self.equipment_name.setStyleSheet("background-color: #484848; color: #ffffff;")
        self.e_vid    = QLabel()
        self.e_vstock = QLabel()
        self.e_vtotal = QLabel()
        self.number_picker_widget = QWidget()

        # Number Picker for total selection
        self.num_layout = QHBoxLayout(self.number_picker_widget)
        self.amount_field = QLineEdit("0")
        self.amount_field.setValidator(QIntValidator())
        self.amount_field.setFixedSize(50, 30)
        self.amount_field.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.amount_field.setStyleSheet("background-color: #484848; color: #ffffff; border-radius: 5px;")

        self.amount_field.textChanged.connect(self.validate_amount_field)

        self.minus_button = QPushButton("-")
        self.minus_button.setFixedSize(30, 30)
        self.minus_button.setStyleSheet("background-color: #484848; color: #ffffff;")
        self.minus_button.clicked.connect(lambda: self.decrease_total())

        self.plus_button = QPushButton("+")
        self.plus_button.setFixedSize(30, 30)
        self.plus_button.setStyleSheet("background-color: #484848; color: #ffffff;")
        self.plus_button.clicked.connect(lambda: self.increase_total())

        self.num_layout.addWidget(self.minus_button)
        self.num_layout.addWidget(self.amount_field)
        self.num_layout.addWidget(self.plus_button)

        # Add field into the grid layout
        grid_layout.addWidget(self.e_vname, 0, 3, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        grid_layout.addWidget(self.equipment_name, 0, 3, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        grid_layout.addWidget(self.e_vid, 1, 3, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        grid_layout.addWidget(self.e_vstock, 2, 3, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        grid_layout.addWidget(self.e_vtotal, 3, 3, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        grid_layout.addWidget(self.number_picker_widget, 3, 3, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        layout.addLayout(grid_layout)

        # Edit Remove Save button section layout (as it is)
        button_section = QHBoxLayout()
        button_section.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Edit Remove Save buttons
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
        self.e_vsave.clicked.connect(lambda: self.save())
        self.e_vcancel.clicked.connect(lambda: self.cancel())

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
        user_header = QLabel("Borrower ID")
        header_layout.addWidget(user_header)

        # Date header
        date_header = QLabel("Return Date")
        header_layout.addWidget(date_header)

        # Amount header
        amount_header = QLabel("Amount")
        header_layout.addWidget(amount_header)

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

    def fetch_borrow_list(self, equipment_id):
        # Format the equipment_id (assuming it's in the format "E0001", strip the "E" and convert to int)
        formatted_e_id = int(equipment_id[1:])
        
        try:
            # Establish a connection to the database
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="test"
            )
            cursor = connection.cursor()

            # SQL query to fetch the borrow list
            query_borrowed_equipment = """
            SELECT be.borrow_id, b.r_id, b.due_date, be.amount
            FROM borrowed_equipment AS be
            JOIN borrow AS b ON be.borrow_id = b.borrow_id
            WHERE be.e_id = %s
            """

            # Execute the query using the formatted equipment ID
            cursor.execute(query_borrowed_equipment, (formatted_e_id,))
            result = cursor.fetchall()

            # Convert result into the required format
            # borrow_list = [(borrow_id, borrower_id, due_date, amount), ...]
            borrow_list = [(row[0], row[1], row[2].strftime("%d/%m/%Y"), row[3]) for row in result]

            return borrow_list

        except mysql.connector.Error as e:
            print(f"An error occurred while fetching equipment content: {e}")
            # Return a default error message with the equipment_id if something goes wrong
            return [(equipment_id, "Error", "", 0)]

        finally:
            # Ensure the connection is closed properly
            if connection.is_connected():
                cursor.close()
                connection.close()
        
    def populate_borrow_list(self,borrow_list):
        # Clear existing equipment items
        while self.borrow_layout.count() > 0: 
            item = self.borrow_layout.takeAt(0)  # Take the first item
            if item.widget():  # If the item is a widget
                item.widget().deleteLater()  # Delete the widget

        # Add equipment items to layout
        for bid, uid, due_date, amount in borrow_list:
            borrow_id = f"B{bid:04d}"  # Format ID
            user_id   = f"R{uid:04d}"  # Format ID
            self.add_borrow(borrow_id, user_id, due_date, amount)

    def add_borrow(self, borrow_id, user_id, due_date, amount):
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

        # Amount 
        amount_label = QLabel(str(amount))
        item_layout.addWidget(amount_label)

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

    def save(self):
        # Get equipment name and total amount
        equipment_name = self.equipment_name.text()
        total_amount = int(self.amount_field.text())

        # Get the original displayed values
        original_name = self.e_vname.text()
        original_total_amount = int(self.e_vtotal.text())
        in_stock_amount = int(self.e_vstock.text())

        # Check for image update
        if self.aepic_path:
            image = open(self.aepic_path, 'rb').read()
            encoded_image = base64.b64encode(image)
        else:
            encoded_image = None

        # Extract numeric part of equipment ID
        id_numeric_part = int(self.e_vid.text()[1:])

        # Track changes to be made in SQL
        changes = []
        update_data = []

        # Compare name change
        if equipment_name != original_name:
            changes.append(f"Name: {original_name} -> {equipment_name}")
            update_data.append(("e_name", equipment_name))

        # Compare total amount change
        if total_amount != original_total_amount:
            changes.append(f"Total Amount: {original_total_amount} -> {total_amount}")
            # Adjust current amount based on the change in total amount
            current_amount_diff = total_amount - original_total_amount
            update_data.append(("e_amount", total_amount))
            update_data.append(("e_curr_amount", (in_stock_amount + current_amount_diff)))

        # Compare image change
        if encoded_image is not None:
            changes.append("Image: Updated")
            update_data.append(("e_img", encoded_image))

        # If no changes, proceed with hiding the fields and resetting the view
        if not changes:
            self.update_content(self.e_vid.text())
            self.e_vedit.show()
            self.e_vremove.show()
            print("No changes detected, exiting save.")
            return

        # Prepare update query and data
        update_query = "UPDATE equipment SET "
        update_query += ", ".join([f"{field} = %s" for field, _ in update_data])
        update_query += " WHERE e_id = %s"
        query_data = [value for _, value in update_data] + [id_numeric_part]

        # Show the confirmation message box with the changes
        changes_text = "\n".join(changes)
        message_box = QMessageBox()
        message_box.setWindowTitle("Confirm Changes")
        message_box.setText(f"The following changes will be applied:\n\n{changes_text}")
        message_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        result = message_box.exec_()

        # If user presses OK, proceed with the update
        if result == QMessageBox.Ok:
            try:
                connection = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="test"
                )
                cursor = connection.cursor()

                # Execute the update query
                cursor.execute(update_query, query_data)

                # Commit the transaction
                connection.commit()

                # Proceed with hiding the fields and resetting the view
                self.update_content(self.e_vid.text())
                self.e_vedit.show()
                self.e_vremove.show()
                print("Save successful, changes applied.")

            except mysql.connector.Error as e:
                print(f"An error occurred while connecting to the database: {e}")

            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

        else:
            # User canceled the action, so reset the view without saving changes
            self.update_content(self.e_vid.text())
            self.e_vedit.show()
            self.e_vremove.show()
            print("Save canceled, no changes applied.")

    def cancel(self):
        # Get equipment name and total amount
        equipment_name = self.equipment_name.text()
        total_amount = int(self.amount_field.text())

        # Get the original displayed values
        original_name = self.e_vname.text()
        original_total_amount = int(self.e_vtotal.text())

        # Check for image update
        if self.aepic_path:
            image = open(self.aepic_path, 'rb').read()
            encoded_image = base64.b64encode(image)
        else:
            encoded_image = None

        # Track changes to be made in SQL
        changes = []

        # Compare name change
        if equipment_name != original_name:
            changes.append(f"Name: {original_name} -> {equipment_name}")

        # Compare total amount change
        if total_amount != original_total_amount:
            changes.append(f"Total Amount: {original_total_amount} -> {total_amount}")

        # Compare image change
        if encoded_image is not None:
            changes.append("Image: Updated")

        if changes:
            # Show the confirmation message box with the changes
            changes_text = "\n".join(changes)
            message_box = QMessageBox()
            message_box.setWindowTitle("Discard Changes?")
            message_box.setText(f"The following changes will be discarded:\n\n{changes_text}")
            message_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            result = message_box.exec_()

            if result == QMessageBox.Ok:
                self.update_content(self.e_vid.text())
                self.e_vedit.show()
                self.e_vremove.show()
                print("changes discarded")
                return
            
            print("cancel")

    def edit(self):
        self.image_button.show()
        self.equipment_name.show()
        self.number_picker_widget.show()
        self.e_vname.hide()
        self.e_vtotal.hide()
        self.e_vedit.hide()
        self.e_vremove.hide()
        self.e_vsave.show()
        self.e_vcancel.show()
        print("edit")

    def remove(self):
        # Check if there are any unreturned equipment
        total_amount = int(self.e_vtotal.text())   # The total equipment count
        current_stock = int(self.e_vstock.text())  # The current stock available

        if current_stock != total_amount:
            # Show a message box indicating that unreturned equipment exist
            message_box = QMessageBox()
            message_box.setWindowTitle("Error")
            message_box.setText("There are unreturned equipment. You cannot delete this equipment.")
            message_box.setIcon(QMessageBox.Warning)
            message_box.setStandardButtons(QMessageBox.Ok)
            message_box.exec_()
            return  # Exit if there are unreturned equipment

        # If all equipment are returned, ask for delete confirmation
        message_box = QMessageBox()
        message_box.setWindowTitle("Confirm Deletion")
        message_box.setText(f"Are you sure you want to delete this equipment?")
        delete_button = message_box.addButton("Delete", QMessageBox.ActionRole)  # Custom "Delete" button
        cancel_button = message_box.addButton(QMessageBox.Cancel)
        message_box.setDefaultButton(cancel_button)

        message_box.exec_()

        # If the user presses cancel, do nothing
        if message_box.clickedButton() == cancel_button:
            return

        # If the user confirms deletion
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="test"
            )
            cursor = connection.cursor()

            # Extract numeric part of equipment ID
            id_numeric_part = int(self.e_vid.text()[1:])

            # SQL Query to delete the equipment from the database
            query = "DELETE FROM equipment WHERE e_id = %s"
            
            # Execute the SQL query
            cursor.execute(query, (id_numeric_part,))

            # Commit the transaction
            connection.commit()

            print("Equipment deleted successfully.")

        except mysql.connector.Error as e:
            # Handle any SQL or connection errors
            print(f"An error occurred while connecting to the database: {e}")

        finally:
            # Ensure the connection is closed properly
            if connection.is_connected():
                cursor.close()
                connection.close()

        # After deletion, return to the equipment page
        self.main_window.show_equipment()
        print("remove")

    def decrease_total(self):
        current_value = int(self.amount_field.text())
        instock_value = int(self.e_vstock.text())
        total_value = int(self.e_vtotal.text())
        restrain_value = total_value - instock_value
        if current_value > restrain_value:
            self.amount_field.setText(str(current_value - 1))

    def increase_total(self):
        current_value = int(self.amount_field.text())
        self.amount_field.setText(str(current_value + 1))

    def validate_amount_field(self):
        current_value = int(self.amount_field.text()) if self.amount_field.text() else 0
        instock_value = int(self.e_vstock.text())
        total_value = int(self.e_vtotal.text())
        restrain_value = total_value - instock_value
        
        # Enforce lower restraint
        if current_value < restrain_value:
            self.amount_field.setText(str(restrain_value))

    def select_image(self):
        self.aepic_path = ''
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.xpm *.jpg)")
        if file_path:
            self.aepic_path = file_path
            pixmap = QPixmap(file_path)
            self.set_rounded_pixmap(self.equipment_image, pixmap)

    def update_content(self, equipment_id):
        content = self.fetch_content(equipment_id)

        self.equipment_image.setFixedSize(300, 300)
        self.equipment_image.setStyleSheet("""border:1px solid #ffffff""")
        self.equipment_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if content[2] is None or len(content[2]) == 0:
            pixmap = self.get_default_image()
            self.equipment_image.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio)) 
        else:
            image_data = QByteArray.fromBase64(content[2])
            pixmap = QPixmap(QImage.fromData(image_data))
            self.set_rounded_pixmap(self.equipment_image,pixmap)

        self.e_vname.setText (content[1])
        self.equipment_name.setText (content[1])
        self.e_vid.setText   (content[0])
        self.e_vstock.setText(str(content[4]))
        self.e_vtotal.setText(str(content[3]))
        self.amount_field.setText(str(content[3]))

        self.populate_borrow_list(self.fetch_borrow_list(equipment_id))

        if self.main_window.uid == "LA0001":
            self.e_vedit.show()
            self.e_vremove.show()
        else:
            self.e_vedit.hide()
            self.e_vremove.hide()

        self.e_vname.show()
        self.e_vtotal.show()
        self.image_button.hide()
        self.number_picker_widget.hide()
        self.equipment_name.hide()
        self.e_vcancel.hide()
        self.e_vsave.hide()

    def fetch_content(self, equipment_id):
        try:
            # Extract numeric part from the equipment_id (e.g., "E0001" -> 1)
            id_numeric_part = int(equipment_id[1:])  # Remove "E" and convert the rest to int

            # Establish a connection to the database
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="test"
            )
            cursor = connection.cursor()

            # SQL query to fetch equipment details based on e_id
            query = "SELECT e_id, e_name, e_img, e_amount, e_curr_amount FROM equipment WHERE e_id = %s"
            cursor.execute(query, (id_numeric_part,))

            # Fetch the result (there should only be one row)
            result = cursor.fetchone()

            # If a result is found, return it as a tuple; otherwise, return a default tuple
            if result:
                e_id, e_name, e_img, e_amount, e_curr_amount = result
                return (f"E{e_id:04d}", e_name, e_img, e_amount, e_curr_amount)
            else:
                # Return default values if no equipment was found with the given ID
                return (equipment_id, "Unknown Name", "", "0", "0")

        except mysql.connector.Error as e:
            print(f"An error occurred while fetching equipment content: {e}")
            return (equipment_id, "Error", "", "0", "0")

        finally:
            # Ensure the connection is closed properly
            if connection:
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