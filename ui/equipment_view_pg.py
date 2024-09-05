from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea,
    QFrame, QSpacerItem, QSizePolicy, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter
import qtawesome as qta 

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
        
        # Widget content area
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Spacer item
        spacer = QWidget()
        spacer.setFixedWidth(20)

        # Details layout
        details_layout = QHBoxLayout()

        # Equipment image
        self.equipment_image = QLabel()
        details_layout.addWidget(self.equipment_image)

        # Add spacer
        details_layout.addWidget(spacer)

        # Details label layout
        details_layout_label = QVBoxLayout()

        # Details label
        name_label  = QLabel("Name:")
        id_label    = QLabel("Equipment ID:")
        stock_label = QLabel("In-Stock:")
        total_label = QLabel("Total:")

        details_layout_label.addWidget(name_label)
        details_layout_label.addWidget(id_label)
        details_layout_label.addWidget(stock_label)
        details_layout_label.addWidget(total_label)

        details_layout.addLayout(details_layout_label)

        # Details content layout
        details_layout_content = QVBoxLayout()

        # Details content
        self.e_vname  = QLabel()
        self.e_vid    = QLabel()
        self.e_vstock = QLabel()
        self.e_vtotal = QLabel()

        details_layout_content.addWidget(self.e_vname)
        details_layout_content.addWidget(self.e_vid)
        details_layout_content.addWidget(self.e_vstock)
        details_layout_content.addWidget(self.e_vtotal)

        details_layout.addLayout(details_layout_content)

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

        self.e_vedit.clicked.connect(lambda: self.edit())
        self.e_vremove.clicked.connect(lambda: self.remove())
        self.e_vsave.clicked.connect(lambda: self.save())

        button_section.addWidget(self.e_vedit)
        button_section.addWidget(self.e_vremove)
        button_section.addWidget(self.e_vsave)

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
        borrow_list = [
            (1,1,'DD/MM/YY',10),
            (2,2,'DD/MM/YY',3),
            (3,4,'DD/MM/YY',5),
            (5,5,'DD/MM/YY',6),
            (6,6,'DD/MM/YY',2),
            (7,7,'DD/MM/YY',3)
        ]

        return borrow_list
    
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
        self.e_vedit.show()
        self.e_vremove.show()
        self.e_vsave.hide()
        print("save")

    def edit(self):
        self.e_vedit.hide()
        self.e_vremove.hide()
        self.e_vsave.show()
        print("edit")

    def remove(self):
        self.main_window.stacked_widget.setCurrentWidget(self.main_window.equipment_page)
        print("remove")

    def update_content(self, equipment_id):
        content = self.fetch_content(equipment_id)

        pixmap = QPixmap(content[2]) if content[2] else self.get_default_image()  # Use default if no image
        self.equipment_image.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))  # Scale image
        self.equipment_image.setFixedSize(300, 300)
        self.equipment_image.setStyleSheet("""border:1px solid #ffffff""")
        self.equipment_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.e_vname.setText (content[1])
        self.e_vid.setText   (content[0])
        self.e_vstock.setText(content[4])
        self.e_vtotal.setText(content[3])

        self.populate_borrow_list(self.fetch_borrow_list(equipment_id))

        self.e_vsave.hide()
        self.e_vedit.show()
        self.e_vremove.show()

    def fetch_content(self, equipment_id):
        #query
        return (equipment_id,"e_name","","e_amount","e_curr_amount")

    def get_default_image(self):
        # Create a default image using a Qt Awesome icon
        icon = qta.icon('fa.file-image-o', color='white')  # Use Qt Awesome icon
        pixmap = QPixmap(180, 180)
        pixmap.fill(Qt.transparent)  # Fill with transparent background
        painter = QPainter(pixmap)
        icon.paint(painter, pixmap.rect())
        painter.end()
        return pixmap
