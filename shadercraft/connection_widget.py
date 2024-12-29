from __future__ import annotations
from uuid import UUID, uuid1

from PySide6.QtCore import QObject, QRectF, QPointF, QLine, Qt
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainter, QPen

from .asserts import assertRef
from .node_widget import NodePin, NodeProxyWidget


class ConnectionWidget(QObject, QGraphicsItem):
    """
    Class encapsulates widget representation of node connection.
    Connection is represented by a line connecting two pins between two different nodes.
    """
    pin_radius: float = 6
    depth_order: int = NodeProxyWidget.depth_order - 10

    def __init__(self, startpin: NodePin, endpin: NodePin, uuid: UUID = uuid1()) -> None:
        QObject.__init__(self, None)
        QGraphicsItem.__init__(self, None)

        self.uuid: UUID = uuid
        self.startpin = startpin
        self.endpin = endpin
        self.setZValue(self.depth_order)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = ...) -> None:
        """Draws the entire widget"""
        assertRef(self.startpin)
        assertRef(self.endpin)

        pen = QPen(Qt.green)
        pen.setWidth(3)
        painter.setPen(pen)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        start = self.startpin.getSceneCenterPos().toPoint()
        end = self.endpin.getSceneCenterPos().toPoint()
        painter.drawLine(QLine(start, end))

    def boundingRect(self) -> QRectF:
        """Get bounding box of this widget"""
        assertRef(self.startpin)
        assertRef(self.endpin)

        start = self.startpin.scenePos()
        end = self.endpin.scenePos()

        left = min(start.x(), end.x())
        right = max(start.x(), end.x())
        top = min(start.y(), end.y())
        bottom = max(start.y(), end.y())
        exp = self.pin_radius * 2

        return QRectF(QPointF(left - exp, top - exp), QPointF(right + exp, bottom + exp))
