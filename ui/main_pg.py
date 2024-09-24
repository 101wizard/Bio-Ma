from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QStackedWidget
from login_pg import LoginPage

from side_nav_bar import SideNavBar
from dashboard_pg import DashboardPage
from equipment_pg import EquipmentPage
from equipment_view_pg import EquipmentViewPage
from add_equipment_pg import AddEquipmentPage
from user_pg import UserPage
from UserFrameTemplate import UserFrameTemplate
from add_user_pg import AddUserPage

from borrow_pg import BorrowPage
from return_pg import ReturnPage

from borrow_view_pg import BorrowViewPage

class MainWindow(QMainWindow):
    def __init__(self, uid):
        super().__init__()

        self.uid = uid
        print(f"Logged in with UID: {self.uid}")

        # Main window settingsw
        self.setWindowTitle("BIO-MA")
        self.setGeometry(100, 100, 1200, 800)

        # Create the main layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        self.setCentralWidget(main_widget)
        
        # Add the side navigation bar
        self.side_nav_bar = SideNavBar()
        main_layout.addWidget(self.side_nav_bar)
        
        # Create the stacked widget
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        main_widget.setLayout(main_layout)
        main_widget.setStyleSheet("background-color: #ADA5A0;")
        
        # Create page instances
        self.dashboard_page = DashboardPage(self)

        self.equipment_page = EquipmentPage(self)
        self.equipment_details = EquipmentViewPage(self)
        self.add_equipment_page = AddEquipmentPage(self)

        self.user_page = UserPage(self)
        self.user_details = UserFrameTemplate(self)
        self.add_user_page = AddUserPage(self)

        self.return_page = ReturnPage(self)
        self.borrow_page = BorrowPage(self)

        self.borrow_details = BorrowViewPage(self)
        
        # Add pages to the stacked widget
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.equipment_page)
        self.stacked_widget.addWidget(self.equipment_details)
        self.stacked_widget.addWidget(self.add_equipment_page)

        self.stacked_widget.addWidget(self.user_page)
        self.stacked_widget.addWidget(self.user_details)
        self.stacked_widget.addWidget(self.add_user_page)

        self.stacked_widget.addWidget(self.return_page)
        self.stacked_widget.addWidget(self.borrow_page)

        self.stacked_widget.addWidget(self.borrow_details)
        
        # Connect signals from the side navigation bar
        self.side_nav_bar.dashboard_selected.connect(self.show_dashboard)
        self.side_nav_bar.equipment_selected.connect(self.show_equipment)
        self.side_nav_bar.add_equipment_selected.connect(self.show_add_equipment)
        self.side_nav_bar.user_selected.connect(self.show_user)
        self.side_nav_bar.add_user_selected.connect(self.show_add_user)
        self.side_nav_bar.profile_selected.connect(self.show_profile)
        self.side_nav_bar.logout_selected.connect(self.logout)
        
        # Show the dashboard page by default
        self.show_dashboard()

    def show_dashboard(self):
        self.stacked_widget.setCurrentWidget(self.dashboard_page)
        self.side_nav_bar.move_indicator(self.side_nav_bar.findChild(QWidget, "Dashboard"))
        self.side_nav_bar.add_equipment_btn.hide()
        self.side_nav_bar.add_user_btn.hide()

    def show_equipment(self):
        self.equipment_page.load_equipment_pg()
        self.stacked_widget.setCurrentWidget(self.equipment_page)
        self.side_nav_bar.move_indicator(self.side_nav_bar.findChild(QWidget, "Equipment"))
        self.side_nav_bar.add_equipment_btn.show()
        self.side_nav_bar.add_user_btn.hide()

    def show_add_equipment(self):
        self.add_equipment_page.loadaddequipment()
        self.stacked_widget.setCurrentWidget(self.add_equipment_page)
        self.side_nav_bar.move_indicator(self.side_nav_bar.findChild(QWidget, "Add Equipment"))

    def show_user(self):
        self.user_page.load_user_pg()
        self.stacked_widget.setCurrentWidget(self.user_page)
        self.side_nav_bar.move_indicator(self.side_nav_bar.findChild(QWidget, "User"))
        self.side_nav_bar.add_user_btn.show()
        self.side_nav_bar.add_equipment_btn.hide()

    def show_add_user(self):
        self.add_user_page.loadadduser()
        self.stacked_widget.setCurrentWidget(self.add_user_page)
        self.side_nav_bar.move_indicator(self.side_nav_bar.findChild(QWidget, "Add User"))

    def show_profile(self):
        self.user_details.update_content(user_id=self.uid, title="Profile")
        self.stacked_widget.setCurrentWidget(self.user_details)
        self.side_nav_bar.move_indicator(self.side_nav_bar.findChild(QWidget, "Profile"))
        self.side_nav_bar.add_equipment_btn.hide()
        self.side_nav_bar.add_user_btn.hide()

    def logout(self):
        self.close()  # Close the main window
        self.login_page = LoginPage()  # Show the login page again
        self.login_page.show()