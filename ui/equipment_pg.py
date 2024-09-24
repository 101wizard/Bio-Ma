from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea,
    QFrame, QSpacerItem, QSizePolicy, QLineEdit
)
from PySide6.QtCore import Qt, QByteArray
from PySide6.QtGui import QPixmap, QPainter, QImage
import qtawesome as qta 
import mysql.connector
import base64


class EquipmentPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window 

        # Main layout
        main_layout = QVBoxLayout(self)

        # Label
        label = QLabel("Equipment")
        label.setStyleSheet("""font-family: "Times [Adobe]";
                                color: #ffffff;
                                padding: 15px;
                                font-size: 20px;
                                font-weight: bold;""")

        # Main Section
        layout = QVBoxLayout(self)

        # Search bar layout
        search_layout = QHBoxLayout()
        
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search equipment...")
        self.search_bar.setStyleSheet("font-size: 15px;")
        self.search_bar.textChanged.connect(self.filter_equipment)  # Connect to search function
        search_layout.addWidget(self.search_bar)

        layout.addLayout(search_layout)

        # Top border for scroll area
        top_border = QWidget()
        top_border.setFixedHeight(1)
        top_border.setStyleSheet("background-color: #ffffff;")
        layout.addWidget(top_border)

        # Scrollable area for equipment list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Hide the vertical scrollbar

        self.equipment_content = QWidget()
        self.equipment_layout = QVBoxLayout(self.equipment_content)
        self.equipment_layout.setContentsMargins(0, 0, 0, 0)
        self.equipment_layout.setSpacing(20)
        self.equipment_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area.setWidget(self.equipment_content)

        layout.addWidget(scroll_area)

        # Bottom border for scroll area
        bottom_border = QWidget()
        bottom_border.setFixedHeight(1)
        bottom_border.setStyleSheet("background-color: #ffffff;")
        layout.addWidget(bottom_border)

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
                                      }""")
        
        main_layout.addWidget(label)
        main_layout.addWidget(widget)

        # Adjust the size of the equipment_content to fit its contents without expanding
        self.equipment_content.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum) 

    def load_equipment_pg(self):
        # Store equipment for filtering
        self.all_equipment = self.fetch_equipment_list()

        # Populate equipment list
        self.populate_equipment_list(self.all_equipment)

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
            self.set_rounded_pixmap(equipment_image,pixmap)
        else:
            pixmap =  self.get_default_image()
            equipment_image.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))  # Scale image

        # Equipment details layout
        details_layout = QVBoxLayout()
        details_layout.setContentsMargins(0, 0, 0, 0)

        # Name and In-Stock
        name_label =  QLabel(f"Name:     {name}")
        stock_label = QLabel(f"In-Stock: {current_amount}/{amount}")
        details_layout.addWidget(name_label)
        details_layout.addWidget(stock_label)

        # Spacer to separate from Equipment ID
        details_layout.addSpacerItem(QSpacerItem(0, 5, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Equipment ID
        id_label = QLabel(f"Equipment ID: {equipment_id}")
        details_layout.addWidget(id_label)

        equipment_layout.addLayout(details_layout)

        # View button
        view_button = QPushButton("View")
        view_button.setStyleSheet("text-decoration: underline;")
        view_button.setFixedSize(50, 180)
        view_button.clicked.connect(lambda: self.view_equipment(equipment_id))
        
        # Add the button to the right side
        equipment_layout.addWidget(view_button, alignment=Qt.AlignRight | Qt.AlignTop)

        layout.addLayout(equipment_layout)

        # Add the frame to the layout
        self.equipment_layout.addWidget(equipment_frame)

        # Add a separator line below the equipment frame
        line = QFrame()
        line.setLineWidth(1)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Plain)
        line.setStyleSheet("background-color: #ffffff;")  # Ensure the color is white and visible
        line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        line.setFixedHeight(1)

        # Add the separator line after the equipment frame
        self.equipment_layout.addWidget(line)

    def get_default_image(self):
        # Create a default image using a Qt Awesome icon
        icon = qta.icon('fa.file-image-o', color='white')  # Use Qt Awesome icon
        pixmap = QPixmap(180, 180)
        pixmap.fill(Qt.transparent)  # Fill with transparent background
        painter = QPainter(pixmap)
        icon.paint(painter, pixmap.rect())
        painter.end()
        return pixmap

    def view_equipment(self, equipment_id):
        self.main_window.equipment_details.update_content(equipment_id=equipment_id)
        self.main_window.stacked_widget.setCurrentWidget(self.main_window.equipment_details)
        print(f"Viewing equipment ID: {equipment_id}")

    def filter_equipment(self):
        search_text = self.search_bar.text().lower()
        # Filter the equipment list based on the current search text
        filtered_equipment = (
            [item for item in self.all_equipment if search_text in item[1].lower()]
            if search_text  # If there is text in the search bar
            else self.all_equipment  # If search bar is empty, show all equipment
        )
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