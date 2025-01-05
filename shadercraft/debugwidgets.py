

from PySide6.QtWidgets import QGraphicsItem, QWidget, QStyleOptionGraphicsItem
from PySide6.QtGui import QPainter, QColor 
from PySide6.QtCore import QRectF, Qt

from .asserts import assertRef


class DebugSquareItem(QGraphicsItem):
    def __init__(self, w: int, h: int, color: QColor = Qt.red):
        super().__init__()
        assertRef(w)
        assertRef(h)

        self.width: int = w
        self.height: int = h
        self.color: QColor = color
        self.setZValue(1000)

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self.color)
        painter.drawRect(self.boundingRect())
