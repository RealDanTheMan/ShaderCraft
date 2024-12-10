from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from PySide6.QtCore import QRectF, Qt

class NodeWidget(QGraphicsItem):
    def __init__(self) -> None:
        super().__init__()
        self.width: float = 128
        self.height: float = 128
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.labelHeight = 20
        self.labelBackground = QColor(92, 92, 92)
        self.labelForeground = QColor(220, 220, 220)
        self.labelText = "Node"
        self.contentBackground = QColor(200, 200, 200)
        self.contentForeground = QColor(250, 250, 250)

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.width, self.height)
    
    def getLabelArea(self) -> QRectF:
        return QRectF(0, 0, self.width, self.labelHeight)
    
    def getContentArea(self) -> QRectF:
        return QRectF(0, self.labelHeight, self.width, self.height - self.labelHeight)
    
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = ...) -> None:
        # Draw label area
        painter.setBrush(self.labelBackground)
        painter.drawRect(self.getLabelArea())
        painter.drawRect
        
        # Draw label text
        text_area = self.getLabelArea().adjusted(10, 0, 0, 0)
        painter.setBrush(self.labelForeground)
        painter.drawText(text_area, Qt.AlignVCenter | Qt.AlignLeft, self.labelText)
        
        # Draw node content area
        painter.setBrush(self.contentBackground)
        painter.drawRect(self.getContentArea())

    def setLabelText(self, text: str) -> None:
        self.labelText = text
