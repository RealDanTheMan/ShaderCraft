from __future__ import annotations
from typing import Optional
from enum import Enum
from uuid import UUID, uuid1
from PySide6.QtGui import QPainter, QColor, QMouseEvent
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from PySide6.QtCore import QRectF, Qt, QPointF, Signal, QObject, Slot


class NodeWidget(QObject, QGraphicsItem):
    positionChanged = Signal(QPointF)

    def __init__(self) -> None:
        QObject.__init__(self, None)
        QGraphicsItem.__init__(self, None)

        self.uuid = uuid1()
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
        self.__inputPins: list[NodePin] = []
        self.__outputPins: list[NodePin] = []

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

    def addInputs(self, ids: list[UUID]) -> None:
        for id in ids:
            pin = NodePin()
            pin.uuid = id
            pin.node_uuid = self.uuid
            pin.role = NodePin.Role.EInput
            pin.setParentItem(self)
            self.__inputPins.append(pin)
        self.updateLayout()

    def addOutputs(self, ids: list[UUID]) -> None:
        for id in ids:
            pin = NodePin()
            pin.uuid = id
            pin.node_uuid = self.uuid
            pin.role = NodePin.Role.EOutput
            pin.setParentItem(self)
            pin.mouseDragBegin.connect(self.onPinDragBegin)
            pin.mouseDragEnd.connect(self.OnPinDragEnd)
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

    def getInputPin(self, uuid: UUID) -> Optional[NodePin]:
        """Get input pin widget of matching UUID"""
        for pin in self.__inputPins:
            if pin.uuid == uuid:
                return pin
        return None

    def getOutputPin(self, uuid: UUID) -> Optional[NodePin]:
        """Get output pin of matchig UUID"""
        for pin in self.__outputPins:
            if pin.uuid == uuid:
                return pin
        return None

    @Slot(QObject)
    def onPinDragBegin(self, pin: QObject) -> None:
        assert (isinstance(pin, NodePin))
        print(f"Pin drag started -> Pin '{pin.getUUID()}'")

    @Slot(QObject)
    def OnPinDragEnd(self, pin: QObject) -> None:
        assert (isinstance(pin, NodePin))
        print(f"Pin drag ended -> Pin '{pin.getUUID()}'")


class NodePin(QObject, QGraphicsItem):
    class Role(Enum):
        ENone = 0
        EInput = 1
        EOutput = 2


    mouseDragBegin = Signal(QObject)
    mouseDragEnd = Signal(QObject)

    def __init__(self):
        """Default constructor"""
        QObject.__init__(self, None)
        QGraphicsItem.__init__(self, None)

        self.role: NodePin.Role = NodePin.Role.ENone
        self.setAcceptHoverEvents(True)
        self.setAcceptDrops(True)
        self.radius: int = 6
        self.foreground: QColor = QColor(0, 200, 0)
        self.foregroundHighlight: QColor = QColor(200, 0, 100)
        self.uuid: UUID = uuid1()
        self.node_uuid: UUID = None
        self.__activeColor: QColor = self.foreground

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = ...) -> None:
        """Draw this pin to the screen"""
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self.__activeColor)
        painter.drawEllipse(0, 0, self.radius*2, self.radius*2)

    def boundingRect(self) -> QRectF:
        """Get bounding area representing the entire node widget"""
        return QRectF(0, 0, self.radius*2, self.radius*2)

    def getRadius(self) -> int:
        """Get pin circle radius in pixels"""
        return self.radius

    def getUUID(self) -> UUID:
        """Get unique identifier of this pin"""
        return self.uuid

    def hoverEnterEvent(self, event: QMouseEvent) -> None:
        """Event handler invoked when the mouse pointer entered pin area"""
        self.__activeColor = self.foregroundHighlight
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QMouseEvent) -> None:
        """Event handler invoked when the mouse pointer leaves pin area"""
        self.__activeColor = self.foreground
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Event handler invoked when the mouse button is pressed while over the pin area"""
        #print("mouse press event")
        self.mouseDragBegin.emit(self)
        #super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Event handler invoked when the mouse button is release while over the pin area"""
        #print("mouse release event")
        self.mouseDragEnd.emit(self)
        #super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Event handler invoked when them mouse pointer changes location wile button is pressed"""
        #print("Mouse move event")
        #super().mouseMoveEvent(event)
