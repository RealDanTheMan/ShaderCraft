from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from PySide6.QtCore import QRectF

class NodeWidget(QGraphicsItem):
    def __init__(self) -> None:
        super().__init__()
        self.width: float = 128
        self.height: float = 128

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.width, self.height)
    
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = ...) -> None:
        painter.setBrush(QColor(255,0,255))
        painter.drawRect(self.boundingRect())