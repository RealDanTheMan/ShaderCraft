from __future__ import annotations
from typing import Optional
from enum import Enum
from dataclasses import dataclass
from uuid import UUID, uuid1
from PySide6.QtGui import QPainter, QColor, QMouseEvent
from PySide6.QtWidgets import (
    QGraphicsItem,
    QStyleOptionGraphicsItem,
    QWidget,
    QGraphicsWidget,
    QGraphicsProxyWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QHBoxLayout,
    QGraphicsView
)
from PySide6.QtCore import QRectF, Qt, QPointF, QPoint, Signal, QObject, Slot

from .asserts import assertRef, assertTrue
from .styles import node_widget_style, node_selected_widget_style

@dataclass
class NodePropetyInfo:
    """
    Convinience class for storing minimal information representing node property.
    UUI: Property identifier
    Lavel: Property label text
    """
    uuid: UUID = None
    label: str = None


class NodePinShapeWidget(QWidget):
    """
    Widget class represneting small round pin visual.
    Pin widgets can be dragged and dropped over other pins to form node connections.
    """
    radius: int = 8

    def __init__(self, node_uuid: UUID, property_uuid: UUID, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.node_uuid = node_uuid
        self.property_uuid = property_uuid
        self.setMinimumSize(self.radius * 3, self.radius * 3)
        self.setMaximumSize(self.minimumSize())

    def paintEvent(self, event) -> None:
        painter: QPainter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(QColor(0, 255, 0))

        x: int = self.rect().center().x() - self.radius
        y: int = self.rect().center().y() - self.radius
        size: int = self.radius * 2
        painter.drawEllipse(x, y, size, size)


class NodePropertyWidget(QWidget):
    """
    Widget class representing node propety.
    Widget property is represented by its pin along with property label text field.
    Node widgets can contain arbitrary number of output or input properties.
    Widget property UUID maps to underlying node property UUID it represents.
    """

    class Role(Enum):
        """
        Enum class representing if its output or input property.
        """
        OUTPUT = 0
        INPUT = 1

    def __init__(
            self,
            node_uuid: UUID,
            name: str,
            property_uuid: UUID,
            role: NodePropertyWidget.Role,
            parent: QWidget = None
    ) -> None:
        super().__init__(parent)
        assertRef(role)
        assertRef(node_uuid)
        assertRef(property_uuid)

        self.name = name
        self.node_uuid = node_uuid
        self.property_uuid = property_uuid
        self.main_layout: QHBoxLayout = QHBoxLayout()
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(2)
        self.label_widget: QLabel = QLabel(self.name, parent=self)
        self.pin_widget: NodePinShapeWidget = NodePinShapeWidget(
            self.node_uuid,
            self.property_uuid,
            parent = self
        )

        if role is NodePropertyWidget.Role.INPUT:
            self.main_layout.addWidget(self.pin_widget)
            self.main_layout.addWidget(self.label_widget)
        elif role is NodePropertyWidget.Role.OUTPUT:
            self.main_layout.addWidget(self.label_widget)
            self.main_layout.addWidget(self.pin_widget)
        else:
            raise RuntimeError("Invalid role argument!")
        self.setLayout(self.main_layout)


class NodeWidget(QWidget):
    """
    Actual widget representation of the node.
    """
    def __init__(
        self,
        node_uuid: UUID,
        inputs: list[NodePropetyInfo],
        outputs: list[NodePropetyInfo],
        parent: QWidget = None
    ):
        super().__init__(parent=parent)
        self.node_uuid = node_uuid
        self.setMinimumSize(160, 160)
        self.setObjectName("NodeWidget")
        self.setStyleSheet(node_widget_style)
        self.root_layout: QVBoxLayout = QVBoxLayout()
        self.root_layout.setSpacing(0)
        self.root_layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(self.root_layout)
        self.property_widgets: list[NodePropertyWidget] = []

        self._createLabelArea()
        self._createNodeArea()

        for in_property in inputs:
            widget: NodePropertyWidget = NodePropertyWidget(
                self.node_uuid,
                in_property.label,
                in_property.uuid,
                NodePropertyWidget.Role.INPUT,
                parent=self
            )
            self.property_widgets.append(widget)
            self.inputs_layout.addWidget(widget)

        for out_property in outputs:
            widget: NodePropertyWidget = NodePropertyWidget(
                self.node_uuid,
                out_property.label,
                out_property.uuid,
                NodePropertyWidget.Role.OUTPUT,
                parent=self
            )
            self.property_widgets.append(widget)
            self.outputs_layout.addWidget(widget)

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
        self.bottom_frame.setMinimumHeight(136)
        self.bottom_layout.addWidget(self.bottom_frame)
        self.root_layout.addLayout(self.bottom_layout)

        self.property_layout: QHBoxLayout = QHBoxLayout()
        self.property_layout.setContentsMargins(4, 4, 4, 4)
        self.property_layout.setSpacing(0)
        self.inputs_layout: QVBoxLayout = QVBoxLayout()
        self.inputs_layout.setContentsMargins(0, 0, 0, 0)
        self.inputs_layout.setSpacing(0)
        self.outputs_layout: QVBoxLayout = QVBoxLayout()
        self.outputs_layout.setContentsMargins(0, 0, 0, 0)
        self.outputs_layout.setSpacing(0)
        self.property_layout.addLayout(self.inputs_layout)
        self.property_layout.addLayout(self.outputs_layout)
        self.bottom_frame.setLayout(self.property_layout)

    def setLabelText(self, text: str) -> None:
        """Set text value of the node label widget"""
        assertRef(text)
        self.node_label.setText(text.upper())

    def setNameText(self, text: str) -> None:
        """Set text value of the node name widget"""
        assertRef(text)
        self.node_name.setText(text)

    def getPinScreenPosition(self, uuid: UUID) -> Optional[QPointF]:
        """Get local postion of pin widget matching given UUID"""
        matches: list[NodePropertyWidget] = [i for i in self.property_widgets if i.property_uuid == uuid]
        if len(matches) > 0:
            assertTrue(len(matches) == 1)
            pin_widget: NodePinShapeWidget = matches[0].pin_widget
            local_pos: QPointF = pin_widget.rect().center()
            return pin_widget.mapToGlobal(local_pos)
        return None


class NodeProxyWidget(QGraphicsWidget):
    """
    Proxy widget class which hosts the actual node widget.
    It handles tranforms and other graphics scene events of the graph its drawned inside.
    """
    positionChanged: Signal = Signal(QPointF)
    selectionChanged: Signal = Signal(bool)
    depth_order: int = 100

    def __init__(self, node_uuid: UUID, inputs: list[NodePropetyInfo], outputs: list[NodePropetyInfo]) -> None:
        super().__init__()
        self.node_uuid: UUID = node_uuid
        self.min_size: int = 160
        self.setMinimumSize(self.min_size, self.min_size)
        self.__widget: NodeWidget = NodeWidget(node_uuid, inputs, outputs)
        self.__proxy: QGraphicsProxyWidget = QGraphicsProxyWidget()
        self.__proxy.setWidget(self.__widget)
        self.__proxy.setParentItem(self)

        self.uuid = uuid1()
        self.setZValue(self.depth_order)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

    def getWidget(self) -> NodeWidget:
        """Get handle to the inner widget object"""
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
                self.__widget.setStyleSheet(node_selected_widget_style)
            else:
                self.__widget.setStyleSheet(node_widget_style)
            self.selectionChanged.emit(value)

        return super().itemChange(change, value)

    def mouseReleaseEvent(self, event):
        """Override for handling mouse releases performed on this widget"""
        super().mouseReleaseEvent(event)
        if event.button is Qt.MouseButton.LeftButton:
            self.positionChanged.emit(self.scenePos())

    def getPinScenePos(self, uuid: UUID) -> Optional[QPointF]:
        """Get graph scene relative position of node pin matching given UUID"""
        assertRef(uuid)
        assertRef(self.getWidget())

        screen_pos: QPoint = self.__widget.getPinScreenPosition(uuid)
        if screen_pos is not None:
            assertRef(self.scene())
            assertTrue(len(self.scene().views()) == 1)

            view: QGraphicsView = self.scene().views()[0]
            view_pos: QPointF = view.mapFromGlobal(screen_pos)
            scene_pos: QPointF = view.mapToScene(view_pos)
            return scene_pos
        return None
