from PySide6.QtWidgets import QPushButton, QSizePolicy, QStyleOptionButton, QStyle, QApplication
from PySide6.QtGui import QPainter
from PySide6.QtCore import QSize, Qt

class OrientablePushButton(QPushButton):
    Horizontal = 0
    VerticalTopToBottom = 1
    VerticalBottomToTop = 2

    def __init__(self, text="", stylesheet="", parent=None):
        super().__init__(text, parent)
        self._orientation = OrientablePushButton.Horizontal
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)

        # Set the stylesheet to the QPushButton
        if stylesheet:
            self.setStyleSheet(stylesheet)

    def setOrientation(self, orientation):
        self._orientation = orientation
        self.update()  # Update the button to trigger a repaint

    def sizeHint(self):
        size_hint = super().sizeHint()
        if self._orientation != OrientablePushButton.Horizontal:
            size_hint = QSize(size_hint.height(), size_hint.width())  # Transpose size hint for vertical
        return size_hint

    def paintEvent(self, event):
        option = QStyleOptionButton()
        self.initStyleOption(option)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # Enable antialiasing for smooth edges

        # Apply rotation based on the orientation
        if self._orientation == OrientablePushButton.VerticalTopToBottom:
            painter.translate(self.width() / 2, self.height() / 2)
            painter.rotate(-90)
            painter.translate(-self.height() / 2, -self.width() / 2)
            option.rect = option.rect.transposed()  # Adjust rect for vertical
        elif self._orientation == OrientablePushButton.VerticalBottomToTop:
            painter.translate(self.width() / 2, self.height() / 2)
            painter.rotate(90)
            painter.translate(-self.height() / 2, -self.width() / 2)
            option.rect = option.rect.transposed()  # Adjust rect for vertical

        # Let the style draw the button
        style = self.style()
        style.drawControl(QStyle.CE_PushButton, option, painter, self)
