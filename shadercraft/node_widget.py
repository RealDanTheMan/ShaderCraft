import uuid
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from PySide6.QtCore import QRectF, Qt, QPointF, Signal, QObject


class NodeWidget(QObject, QGraphicsItem):
    positionChanged = Signal(QPointF)

    def __init__(self) -> None:
        QObject.__init__(self, None)
        QGraphicsItem.__init__(self, None)

        self.uuid = uuid.uuid1()
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
        self.__inputPins: [NodePin] = []
        self.__outputPins: [NodePin] = []

    def boundingRect(self) -> QRectF:
        """Get bounding area representing the entire node widget"""
        return QRectF(0, 0, self.width, self.height)

    def getLabelArea(self) -> QRectF:
        """Get bounding area representing the label portion of the node widget"""
        return QRectF(0, 0, self.width, self.labelHeight)

    def getContentArea(self) -> QRectF:
        """Get bounding area representing the content portion of the node widget"""
        return QRectF(0, self.labelHeight, self.width, self.height - self.labelHeight)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = ...) -> None:
        """Draws the entire widget"""
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw label area
        painter.setBrush(self.labelBackground)
        painter.drawRect(self.getLabelArea())

        # Draw label text
        text_area = self.getLabelArea().adjusted(10, 0, 0, 0)
        painter.setBrush(self.labelForeground)
        painter.drawText(text_area, Qt.AlignVCenter | Qt.AlignLeft, self.labelText)

        # Draw node content area
        painter.setBrush(self.contentBackground)
        painter.drawRect(self.getContentArea())

    def itemChange(self, change, value):
        """Override for handling internal widget changes"""
        if change == QGraphicsItem.ItemPositionChange:
            self.positionChanged.emit(self.scenePos())

        return super().itemChange(change, value)

    def mouseReleaseEvent(self, event):
        """Override for handling mouse releases performed on this widget"""
        super().mouseReleaseEvent(event)
        self.positionChanged.emit(self.scenePos())

    def setLabelText(self, text: str) -> None:
        """Update text drawn in the label area of the widget"""
        self.labelText = text

    def addInputs(self, ids: [uuid.UUID]) -> None:
        for id in ids:
            pin = NodePin()
            pin.uuid = id
            pin.setParentItem(self)
            self.__inputPins.append(pin)
        self.updateLayout()

    def addOutputs(self, ids: [uuid.UUID]) -> None:
        for id in ids:
            pin = NodePin()
            pin.uuid = id
            pin.setParentItem(self)
            self.__outputPins.append(pin)
        self.updateLayout()

    def updateLayout(self):
        pin_padding = 6
        offset = self.labelHeight + pin_padding
        for pin in self.__inputPins:
            pin.setPos(-pin.getRadius(), offset)
            offset += pin.boundingRect().height() + pin_padding

        # Output pins layout
        offset = self.labelHeight + pin_padding
        for pin in self.__outputPins:
            pin.setPos(self.getContentArea().width() - pin.getRadius(), offset)
            offset += pin.boundingRect().height() + pin_padding


class NodePin(QObject, QGraphicsItem):
    def __init__(self):
        QObject.__init__(self, None)
        QGraphicsItem.__init__(self, None)

        self.radius = 6
        self.foreground = QColor(0, 200, 0)
        self.uuid = uuid.uuid1()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = ...) -> None:
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self.foreground)
        painter.drawEllipse(0, 0, self.radius*2, self.radius*2)

    def boundingRect(self) -> QRectF:
        """Get bounding area representing the entire node widget"""
        return QRectF(0, 0, self.radius*2, self.radius*2)

    def getRadius(self) -> int:
        return self.radius

    def getUUID(self) -> uuid.UUID:
        return self.uuid
