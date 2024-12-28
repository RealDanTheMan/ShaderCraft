from __future__ import annotations
from typing import Optional
from enum import Enum
from uuid import UUID, uuid1
from PySide6.QtGui import QPainter, QColor, QMouseEvent, QPen
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from PySide6.QtCore import QRectF, Qt, QPointF, Signal, QObject, Slot

from .asserts import assertRef, assertTrue


class NodeWidget(QObject, QGraphicsItem):
    positionChanged = Signal(QPointF)
    selectionChanged = Signal(bool)

    def __init__(self) -> None:
        QObject.__init__(self, None)
        QGraphicsItem.__init__(self, None)

        self.uuid = uuid1()
        self.width: float = 128
        self.height: float = 128
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.labelHeight = 20
        self.labelBackground = QColor(92, 92, 92)
        self.labelForeground = QColor(220, 220, 220)
        self.labelText = "Node"
        self.contentBackground = QColor(200, 200, 200)
        self.contentForeground = QColor(250, 250, 250)
        self.border_color_idle: QColor = QColor(20, 20, 20)
        self.border_color_selected: QColor = QColor(140, 50,50)
        self.border_color: QColor = self.border_color_idle
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

        # Draw border around the node
        pen:  QPen = QPen(self.border_color)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(self.boundingRect())

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

        if change == QGraphicsItem.ItemSelectedChange:
            if value:
                self.border_color = self.border_color_selected
            else:
                self.border_color = self.border_color_idle
            self.selectionChanged.emit(value)

        return super().itemChange(change, value)

    def mouseReleaseEvent(self, event):
        """Override for handling mouse releases performed on this widget"""
        super().mouseReleaseEvent(event)
        if event.button is Qt.MouseButton.LeftButton:
            self.positionChanged.emit(self.scenePos())

    def setLabelText(self, text: str) -> None:
        """Update text drawn in the label area of the widget"""
        self.labelText = text

    def addInputs(self, ids: list[UUID]) -> None:
        """Add node input pins"""
        for input_id in ids:
            pin = NodePin()
            pin.uuid = input_id
            pin.node_uuid = self.uuid
            pin.role = NodePin.Role.INPUT
            pin.setParentItem(self)
            self.__inputPins.append(pin)
        self.updateLayout()

    def addOutputs(self, ids: list[UUID]) -> None:
        """Add node output pins"""
        for output_id in ids:
            pin = NodePin()
            pin.uuid = output_id
            pin.node_uuid = self.uuid
            pin.role = NodePin.Role.OUTPUT
            pin.setParentItem(self)
            pin.mouseDragBegin.connect(self.onPinDragBegin)
            pin.mouseDragEnd.connect(self.onPinDragEnd)
            self.__outputPins.append(pin)
        self.updateLayout()

    def updateLayout(self):
        """Regenerate this node widget layout"""
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
        """Event handler invoked when node pin begins to be dragged by mouse pointer"""
        assertTrue(isinstance(pin, NodePin))
        print(f"Pin drag started -> Pin '{pin.getUUID()}'")

    @Slot(QObject)
    def onPinDragEnd(self, pin: QObject) -> None:
        """Event handler invoked when dragged pin is dropped"""
        assertTrue(isinstance(pin, NodePin))
        print(f"Pin drag ended -> Pin '{pin.getUUID()}'")


class NodePin(QObject, QGraphicsItem):
    """
    Class encapsulating custin graphics widget representing node pin.
    Node pins can be dragged over pins of other nodes to form connections.
    """
    class Role(Enum):
        """Enum class representing pin role"""
        NONE = 0
        INPUT = 1
        OUTPUT = 2

    mouseDragBegin = Signal(QObject)
    mouseDragEnd = Signal(QObject)

    def __init__(self):
        """Default constructor"""
        QObject.__init__(self, None)
        QGraphicsItem.__init__(self, None)

        self.role: NodePin.Role = NodePin.Role.NONE
        self.setAcceptHoverEvents(True)
        self.setAcceptDrops(True)
        self.radius: int = 6
        self.foreground: QColor = QColor(0, 200, 0)
        self.foreground_hover: QColor = QColor(200, 0, 100)
        self.uuid: UUID = uuid1()
        self.node_uuid: UUID = None
        self.__current_color: QColor = self.foreground

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = ...) -> None:
        """Draw this pin to the screen"""
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self.__current_color)
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
        self.__current_color = self.foreground_hover
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QMouseEvent) -> None:
        """Event handler invoked when the mouse pointer leaves pin area"""
        self.__current_color = self.foreground
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Event handler invoked when the mouse button is pressed while over the pin area"""
        assertRef(event)
        self.mouseDragBegin.emit(self)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Event handler invoked when the mouse button is release while over the pin area"""
        assertRef(event)
        self.mouseDragEnd.emit(self)

    def getSceneCenterPos(self) -> QPointF:
        """Get position of the center of the pin in scene coordinates"""
        x = self.scenePos().x() + float(self.radius)
        y = self.scenePos().y() + float(self.radius)
        return QPointF(x, y)
