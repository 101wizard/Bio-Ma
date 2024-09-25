from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

class ReturnPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window 

        layout = QVBoxLayout(self)

        # Example content
        layout.addWidget(QLabel("Return Page"))

        