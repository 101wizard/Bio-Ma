# side_nav_bar.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PySide6.QtCore import Signal, QPropertyAnimation, QRect, QSize, QEasingCurve
import qtawesome as qta

class SideNavBar(QWidget):
    # Signals for navigation
    dashboard_selected = Signal()
    equipment_selected = Signal()
    add_equipment_selected = Signal()
    user_selected = Signal()
    add_user_selected = Signal()
    profile_selected = Signal()
    logout_selected = Signal()

    def __init__(self):
        super().__init__()

        # Set up the main layout
        layout = QVBoxLayout()
        horiz_lay = QHBoxLayout()
        self.setLayout(layout)
        self.setFixedWidth(150)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 15px;
                text-align: left;
                color: #ffffff;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #383838;
            }
            QLabel {
                font-family: "Times [Adobe]";
                color: #ffffff;
                padding: 15px;
                font-size: 16px;
            }
        """)

        # Create the logo at the top
        self.exp_ctr = QPushButton()
        self.exp_ctr.setIcon(qta.icon('ei.lines', color='white'))
        self.lable = QLabel('BIOMA')
        horiz_lay.addWidget(self.lable)
        horiz_lay.addStretch()
        horiz_lay.addWidget(self.exp_ctr)

        # Create buttons with icons and set object names
        self.dashboard_btn = self.create_nav_button("Dashboard", qta.icon('ri.home-3-line', color='white'))
        self.equipment_btn = self.create_nav_button("Manage\nEquipment", qta.icon('mdi.flask-empty-outline', color='white'))
        self.add_equipment_btn = self.create_add_button("Add\nEquipment", qta.icon('mdi.flask-empty-plus-outline', color='white'))
        self.user_btn = self.create_nav_button("Manage\nUser", qta.icon('ph.users-four-light', color='white'))
        self.add_user_btn = self.create_add_button("Add\nUser", qta.icon('ri.user-add-line', color='white'))
        self.profile_btn = self.create_nav_button("Profile", qta.icon('fa.user-circle-o', color='white'))
        self.logout_btn = self.create_nav_button("Logout", qta.icon('mdi6.logout', color='white'))

        # Set object names for the buttons
        self.dashboard_btn.setObjectName("Dashboard")
        self.equipment_btn.setObjectName("Equipment")
        self.add_equipment_btn.setObjectName("Add Equipment")
        self.user_btn.setObjectName("User")
        self.add_user_btn.setObjectName("Add User")
        self.profile_btn.setObjectName("Profile")
        self.logout_btn.setObjectName("Logout")

        # Hide Add buttons
        self.add_equipment_btn.hide()
        self.add_user_btn.hide()

        # Add buttons to the navigation layout
        nav_layout = QVBoxLayout()
        nav_layout.addLayout(horiz_lay)
        nav_layout.addWidget(self.dashboard_btn)
        nav_layout.addWidget(self.equipment_btn)
        nav_layout.addWidget(self.add_equipment_btn)
        nav_layout.addWidget(self.user_btn)
        nav_layout.addWidget(self.add_user_btn)

        nav_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        nav_layout.addWidget(self.profile_btn)
        nav_layout.addWidget(self.logout_btn)

        # Convert layout into widget
        sidemenu = QWidget()
        sidemenu.setLayout(nav_layout)
        sidemenu.setStyleSheet("""background-color: #303030; 
                                border-top-right-radius: 10px;
                                border-bottom-right-radius: 10px;""")

        # Add widget to layout
        layout.addWidget(sidemenu)
        self.setFixedWidth(200)

        # Connect button for expand and contract
        self.exp_ctr.clicked.connect(self.expand_contract)

        # Connect buttons to their respective signals
        self.dashboard_btn.clicked.connect(self.dashboard_selected.emit)
        self.equipment_btn.clicked.connect(self.equipment_selected.emit)
        self.add_equipment_btn.clicked.connect(self.add_equipment_selected.emit)
        self.user_btn.clicked.connect(self.user_selected.emit)
        self.add_user_btn.clicked.connect(self.add_user_selected.emit)
        self.profile_btn.clicked.connect(self.profile_selected.emit)
        self.logout_btn.clicked.connect(self.logout_selected.emit)

    def create_nav_button(self, text, icon):
        button = QPushButton(text)
        button.setIcon(icon)
        button.setIconSize(QSize(24, 24))
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                text-align: left;
                padding-left: 10px;
                font-size: 16px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #383838;
            }
        """)
        return button
    
    def create_add_button(self, text, icon):
        button = QPushButton(text)
        button.setIcon(icon)
        button.setIconSize(QSize(24, 24))
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border-bottom: 1px solid #ffffff;
                border-right: 1px solid #ffffff;
                border-top-right-radius: 0px;
                text-align: left;
                padding-left: 10px;
                font-size: 16px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #383838;
            }
        """)
        return button

    def move_indicator(self, widget):
        if widget:
            # Reset all buttons to their normal style
            for button in [self.dashboard_btn, self.equipment_btn, self.user_btn, self.profile_btn, self.logout_btn]:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                        text-align: left;
                        padding-left: 10px;
                        font-size: 16px;
                        color: #ffffff;
                    }
                    QPushButton:hover {
                        background-color: #383838;
                    }
                """)
            for button in [self.add_equipment_btn, self.add_user_btn]:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border-bottom: 1px solid #ffffff;
                        border-right: 1px solid #ffffff;
                        border-top-right-radius: 0px;
                        text-align: left;
                        padding-left: 10px;
                        font-size: 16px;
                        color: #ffffff;
                    }
                    QPushButton:hover {
                        background-color: #383838;
                    }
                """)

            # Apply the selected style to the current button
            widget.setStyleSheet("""
                QPushButton {
                    background-color: #444444;
                    border-left: 3px solid #ffffff;
                    text-align: left;
                    padding-left: 12px;
                    font-size: 16px;
                    color: #ffffff;
                }
            """)

    def expand_contract(self):
        if self.lable.isHidden():
            self.lable.show()
            self.dashboard_btn.setText("Dashboard")
            self.equipment_btn.setText("Equipment")
            self.add_equipment_btn.setText("Add")
            self.user_btn.setText("User")
            self.add_user_btn.setText("Add")
            self.profile_btn.setText("Profile")
            self.logout_btn.setText("Logout")
            self.setFixedWidth(200)
            print('expand')
        else:
            self.lable.hide()
            self.dashboard_btn.setText("")
            self.equipment_btn.setText("")
            self.add_equipment_btn.setText("")
            self.user_btn.setText("")
            self.add_user_btn.setText("")
            self.profile_btn.setText("")
            self.logout_btn.setText("")
            self.setFixedWidth(80)
            print('contract')
