from PySide6.QtWidgets import QWidget, QPushButton, QSizePolicy, QVBoxLayout, QApplication
from PySide6.QtGui import QPainter
from PySide6.QtCore import QSize, Qt

class Rotate(QWidget):
    Horizontal = 0
    VerticalTopToBottom = 1
    VerticalBottomToTop = 2

    def __init__(self, button: QPushButton, orientation=Horizontal, parent=None):
        super().__init__(parent)
        self.button = button
        self._orientation = orientation

        # Create a layout to hold the button
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.button)

        self.updateSize()  # Set the initial size based on the button

    def updateSize(self):
        """Update the widget size based on the button orientation."""
        if self._orientation in (Rotate.VerticalTopToBottom, Rotate.VerticalBottomToTop):
            self.setMinimumSize(self.button.sizeHint().height(), self.button.sizeHint().width())
        else:
            self.setMinimumSize(self.button.sizeHint())

    def setOrientation(self, orientation):
        self._orientation = orientation
        self.updateSize()  # Update the size on orientation change
        self.update()  # Update the widget to trigger a repaint

    def sizeHint(self):
        # Return the size hint of the button, potentially adjusted for rotation
        if self._orientation in (Rotate.VerticalTopToBottom, Rotate.VerticalBottomToTop):
            return QSize(self.button.sizeHint().height(), self.button.sizeHint().width())
        return self.button.sizeHint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.save()  # Save the current painter state

        # Set rotation based on the orientation
        if self._orientation == Rotate.VerticalTopToBottom:
            painter.translate(self.width() / 2, self.height() / 2)
            painter.rotate(-90)
            painter.translate(-self.height() / 2, -self.width() / 2)
        elif self._orientation == Rotate.VerticalBottomToTop:
            painter.translate(self.width() / 2, self.height() / 2)
            painter.rotate(90)
            painter.translate(-self.height() / 2, -self.width() / 2)

        # Paint the button directly on the widget
        self.button.setGeometry(self.rect())
        self.button.render(painter, self.rect().topLeft(), self.rect())

        painter.restore()  # Restore the painter state

# Example usage
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QWidget, QVBoxLayout

    app = QApplication(sys.argv)

    window = QWidget()
    layout = QVBoxLayout(window)

    # Create a QPushButton
    button = QPushButton("Researcher")
    button.setStyleSheet("""background-color: #303030; 
                            border-radius: 0;
                            font-size: 15px;
                            border-top-left-radius: 10px;
                            color: #ffffff;""")
    button.setFixedHeight(40)
    button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    # Create a Rotate widget with the button
    button_rotated = Rotate(button, Rotate.VerticalTopToBottom)  # Rotate the button

    layout.addWidget(button_rotated)
    window.setLayout(layout)

    window.show()
    sys.exit(app.exec())
