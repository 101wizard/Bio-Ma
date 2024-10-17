from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea,
    QFrame, QSpacerItem, QSizePolicy, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter
import qtawesome as qta 
import mysql.connector

class BorrowViewPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        # Main layout
        main_layout = QVBoxLayout(self)

        # Title Label
        self.title_label = QLabel('Borrow Information')  # Assign as instance variable
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

        spacerv = QWidget()
        spacerv.setFixedHeight(10)

        # Details layout
        details_layout = QHBoxLayout()

        # Add spacer
        details_layout.addWidget(spacer)

        # IDs label layout
        ids_layout_label = QVBoxLayout()

        # IDs label
        borrow_label = QLabel("Borrow ID:")
        borrower_label = QLabel("Borrower ID")
        approver_label = QLabel("Approver ID")

        ids_layout_label.addWidget(borrow_label)
        ids_layout_label.addWidget(spacerv)
        ids_layout_label.addWidget(borrower_label)
        ids_layout_label.addWidget(spacerv)
        ids_layout_label.addWidget(approver_label)
        ids_layout_label.addWidget(spacerv)

        details_layout.addLayout(ids_layout_label)

        # IDs content layout
        IDs_layout = QVBoxLayout()

        # Details content
        self.b_vborrow_id = QLabel()
        self.b_vborrower_id = QPushButton()
        self.b_vborrower_id.setStyleSheet("text-decoration: underline; text-align: left; padding-left: 0;")
        self.b_vborrower_id.setFixedSize(50, 20)
        self.b_vapprover_id = QPushButton()
        self.b_vapprover_id.setStyleSheet("text-decoration: underline; text-align: left; padding-left: 0;")
        self.b_vapprover_id.setFixedSize(50, 20)
        
        IDs_layout.addWidget(self.b_vborrow_id )
        IDs_layout.addWidget(spacerv)
        IDs_layout.addWidget(self.b_vborrower_id )
        IDs_layout.addWidget(spacerv)
        IDs_layout.addWidget(self.b_vapprover_id)
        IDs_layout.addWidget(spacerv)

        details_layout.addLayout(IDs_layout)

        # Add spacer
        details_layout.addWidget(spacer)

        # Date label layout
        date_layout_label = QVBoxLayout()

        # Date label
        borrow_date_label  = QLabel("Borrow Date:")
        due_date_label     = QLabel("Due Date:")

        date_layout_label.addWidget(borrow_date_label)
        date_layout_label.addWidget(spacerv)
        date_layout_label.addWidget(due_date_label)
        date_layout_label.addWidget(spacerv)
        date_layout_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        details_layout.addLayout(date_layout_label)

        # Date content layout
        date_layout_content = QVBoxLayout()

        # Date content
        self.borrow_date  = QLabel()
        self.due_date    = QLabel()

        date_layout_content.addWidget(self.borrow_date)
        date_layout_content.addWidget(spacerv)
        date_layout_content.addWidget(self.due_date)
        date_layout_content.addWidget(spacerv)
        date_layout_content.setAlignment(Qt.AlignmentFlag.AlignTop)

        details_layout.addLayout(date_layout_content)

        layout.addLayout(details_layout)

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

        # Equipment-ID header
        equipment_header = QLabel("Equipment ID")
        header_layout.addWidget(equipment_header)

        # Equipment Name header
        equipment_name_header = QLabel("Equipment Name")
        header_layout.addWidget(equipment_name_header)

        # Amount header
        amount_header = QLabel("Amount")
        header_layout.addWidget(amount_header)
        
        layout.addWidget(header_frame)

        # Scrollable area for list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Hide the vertical scrollbar
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable horizontal scrolling

        self.elist_content = QWidget()
        self.elist_layout = QVBoxLayout(self.elist_content)
        self.elist_layout.setContentsMargins(0, 0, 0, 0)
        self.elist_layout.setSpacing(20)
        self.elist_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area.setWidget(self.elist_content)

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
        self.elist_content.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum) 

        self.content_layout = layout
    
    def populate_b_vequipment_list(self, equipment_list):
        # Clear existing equipment items
        while self.elist_layout.count() > 0: 
            item = self.elist_layout.takeAt(0)  # Take the first item
            if item.widget():  # If the item is a widget
                item.widget().deleteLater()  # Delete the widget

        # Add equipment items to layout
        for eid, amount, equipment_name in equipment_list:
            equipment_id = f"E{eid:04d}"  # Format ID
            self.add_equipment(equipment_id, amount, equipment_name)

    def add_equipment(self, equipment_id, amount, equipment_name):
        item_frame = QFrame()
        item_frame.setFixedHeight(40)  # Consistent height for each item
        layout = QVBoxLayout(item_frame)
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(10, 0, 10, 0)
        item_layout.setSpacing(10)

        # Equipment-ID 
        equipment_id_label = QPushButton(equipment_id)
        equipment_id_label.setStyleSheet("text-decoration: underline; text-align: left; padding-left: 0;")
        equipment_id_label.setFixedHeight(20)
        equipment_id_label.clicked.connect(lambda: self.view_equipment(equipment_id))
        item_layout.addWidget(equipment_id_label)

        # Equipment Name
        equipment_label = QLabel(equipment_name)
        item_layout.addWidget(equipment_label)

        # Amount
        amount_label = QLabel(str(amount))
        item_layout.addWidget(amount_label)

        layout.addLayout(item_layout)

        # Add the frame to the layout
        self.elist_layout.addWidget(item_frame)

    def view_equipment(self, equipment_id):
        self.main_window.equipment_details.update_content(equipment_id=equipment_id)
        self.main_window.stacked_widget.setCurrentWidget(self.main_window.equipment_details)
        self.main_window.side_nav_bar.move_indicator(self.main_window.side_nav_bar.findChild(QWidget, "Equipment"))
        self.main_window.side_nav_bar.add_equipment_btn.show()
        self.main_window.side_nav_bar.add_user_btn.hide()
        print(f"Viewing equipment ID: {equipment_id}")

    def show_view_borrower(self, uid):
        self.main_window.user_details.update_content(user_id=uid, title="User : Researcher")
        self.main_window.stacked_widget.setCurrentWidget(self.main_window.user_details)
        self.main_window.side_nav_bar.move_indicator(self.main_window.side_nav_bar.findChild(QWidget, "User"))
        self.main_window.side_nav_bar.add_user_btn.show()
        self.main_window.side_nav_bar.add_equipment_btn.hide()
        print(f"Viewing Borrower ID: {uid}")

    def show_view_approver(self, uid):
        self.main_window.user_details.update_content(user_id=uid, title="User : Lab Assistant")
        self.main_window.stacked_widget.setCurrentWidget(self.main_window.user_details)
        self.main_window.side_nav_bar.move_indicator(self.main_window.side_nav_bar.findChild(QWidget, "User"))
        self.main_window.side_nav_bar.add_user_btn.show()
        self.main_window.side_nav_bar.add_equipment_btn.hide()
        print(f"Viewing Approver ID: {uid}")

    def update_content(self, borrow_id):
        borrow_content, equipment_list = self.fetch_content(borrow_id)

        self.b_vborrow_id.setText  (borrow_id)
        self.b_vborrower_id.setText(f"R{borrow_content[1]:04d}")
        self.b_vapprover_id.setText(f"LA{borrow_content[2]:04d}")

        self.b_vborrower_id.clicked.connect(lambda: self.show_view_borrower(f"R{borrow_content[1]:04d}"))
        self.b_vapprover_id.clicked.connect(lambda: self.show_view_approver(f"LA{borrow_content[2]:04d}"))

         # Format the borrow_date and due_date as strings
        borrow_date_str = borrow_content[3].strftime("%d/%m/%Y")  # Format the date as DD/MM/YYYY
        due_date_str = borrow_content[4].strftime("%d/%m/%Y")     # Format the date as DD/MM/YYYY

        # Set the text of the QLabel widgets with the formatted string
        self.borrow_date.setText(borrow_date_str)
        self.due_date.setText   (due_date_str)

        self.populate_b_vequipment_list(equipment_list)

    def fetch_content(self, borrow_id):
        try:
            formatted_borrow_id = int(borrow_id[1:])
            print(f"Fetching content for borrow_id: {formatted_borrow_id}")

            # Step 2: Connect to the database
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="test"
            )
            cursor = connection.cursor()

            # Step 3: Fetch borrow content from 'borrow' table
            borrow_query = """
                SELECT borrow_id, r_id, la_id, borrow_date, due_date
                FROM borrow
                WHERE borrow_id = %s
            """
            cursor.execute(borrow_query, (formatted_borrow_id,))
            borrow_content = cursor.fetchone()

            if not borrow_content:
                print(f"No borrow record found for borrow_id: {formatted_borrow_id}")
                return None, []

            # Step 4: Fetch equipment list from 'borrowed_equipment' and 'equipment' tables
            equipment_query = """
                SELECT be.e_id, be.amount, e.e_name
                FROM borrowed_equipment be
                JOIN equipment e ON be.e_id = e.e_id
                WHERE be.borrow_id = %s
            """
            cursor.execute(equipment_query, (formatted_borrow_id,))
            equipment_list = cursor.fetchall()

            # Step 5: Process the equipment list into (e_id, amount, e_name) format
            processed_equipment_list = [
                (e_id, amount, e_name)
                for e_id, amount, e_name in equipment_list
            ]

            # Return borrow content and processed equipment list
            return borrow_content, processed_equipment_list

        except mysql.connector.Error as e:
            print(f"Database error while fetching content: {e}")
            return None, []

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()