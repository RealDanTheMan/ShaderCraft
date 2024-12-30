from __future__ import annotations
from typing import Optional
from enum import Enum
from uuid import UUID, uuid1
from PySide6.QtGui import QPainter, QColor, QMouseEvent
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget, QGraphicsWidget, QGraphicsProxyWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import QRectF, Qt, QPointF, Signal, QObject, Slot

from .asserts import assertRef, assertTrue
from .styles import node_widget_style

class NodeWidget(QWidget):
    """
    Actual widget representation of the node.
    """
    def __init__(self):
        super().__init__()
        self.setMinimumSize(128, 128)
        self.setObjectName("NodeWidget")
        self.setStyleSheet(node_widget_style)
        self.root_layout: QVBoxLayout = QVBoxLayout()
        self.root_layout.setSpacing(0)
        self.root_layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.root_layout)

        self._createLabelArea()
        self._createNodeArea()

    def _createLabelArea(self) -> None:
        self.label_layout: QVBoxLayout = QVBoxLayout()
        self.label_layout.setSpacing(0)
        self.label_layout.setContentsMargins(0, 0, 0, 0)
        self.label_frame: QFrame = QFrame()
        self.label_frame.setObjectName("NodeLabelArea")
        self.label_frame.setLayout(QVBoxLayout())
        self.label_frame.layout().setSpacing(0)
        self.label_frame.layout().setContentsMargins(4, 4, 4, 4)
        self.node_label: QLabel = QLabel("Node Label")
        self.node_label.setObjectName("NodeLabelText")
        self.label_frame.layout().addWidget(self.node_label)
        self.node_name: QLabel = QLabel("Node Name")
        self.node_name.setObjectName("NodeNameText")
        self.label_frame.layout().addWidget(self.node_name)
        self.label_layout.addWidget(self.label_frame)
        self.root_layout.addLayout(self.label_layout)

    def _createNodeArea(self) -> None:
        self.bottom_layout: QVBoxLayout = QVBoxLayout()
        self.bottom_frame: QFrame = QFrame()
        self.bottom_frame.setObjectName("NodeArea")
        self.bottom_frame.setMinimumHeight(100)
        self.bottom_layout.addWidget(self.bottom_frame)
        self.root_layout.addLayout(self.bottom_layout)

    def setLabelText(self, text: str) -> None:
        """Set text value of the node label widget"""
        assertRef(text)
        self.node_label.setText(text.upper())

    def setNameText(self, text: str) -> None:
        """Set text value of the node name widget"""
        assertRef(text)
        self.node_name.setText(text)


class NodeProxyWidget(QGraphicsWidget):
    """
    Proxy widget class which hosts the actual node widget.
    It handles tranforms and other graphics scene events of the graph its drawned inside.
    """
    positionChanged = Signal(QPointF)
    selectionChanged = Signal(bool)
    depth_order: int = 100

    def __init__(self) -> None:
        super().__init__()
        self.min_size: int = 128
        self.setMinimumSize(self.min_size, self.min_size)
        self.__widget: NodeWidget = NodeWidget()
        self.__proxy: QGraphicsProxyWidget = QGraphicsProxyWidget()
        self.__proxy.setWidget(self.__widget)
        self.__proxy.setParentItem(self)

        self.uuid = uuid1()
        self.setZValue(self.depth_order)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.labelHeight = 32
        self.__inputPins: list[NodePin] = []
        self.__outputPins: list[NodePin] = []

    def getWidget(self) -> NodeWidget:
        return self.__widget

    def boundingRect(self) -> QRectF:
        """Get bounding area representing the entire node widget"""
        return QRectF(0, 0, self.min_size, self.min_size)

    def itemChange(self, change, value):
        """Override for handling internal widget changes"""
        if change == QGraphicsItem.ItemPositionChange:
            self.positionChanged.emit(self.scenePos())

        if change == QGraphicsItem.ItemSelectedChange:
            if value:
                # TODO: Set widget selection color
                pass
            else:
                # TODO: Set widget dormant color
                pass
            self.selectionChanged.emit(value)

        return super().itemChange(change, value)

    def mouseReleaseEvent(self, event):
        """Override for handling mouse releases performed on this widget"""
        super().mouseReleaseEvent(event)
        if event.button is Qt.MouseButton.LeftButton:
            self.positionChanged.emit(self.scenePos())

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
            pin.setPos(self.min_size - pin.getRadius(), offset)
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
    depth_order: int = NodeProxyWidget.depth_order + 10

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
        self.setZValue(self.depth_order)
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
