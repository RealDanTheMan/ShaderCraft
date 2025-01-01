from __future__ import annotations
from uuid import UUID, uuid1

from PySide6.QtCore import QObject, QRectF, QPointF, QLine, Qt
from PySide6.QtWidgets import QGraphicsItem, QWidget
from PySide6.QtGui import QPainter, QPen

from .asserts import assertRef
from .node_widget import NodeProxyWidget


class ConnectionWidget(QObject, QGraphicsItem):
    """
    Class encapsulates widget representation of node connection.
    Connection is represented by a line connecting two pins between two different nodes.
    """
    pin_radius: float = 6
    depth_order: int = NodeProxyWidget.depth_order - 10

    def __init__(self, owner: UUID, start: QPointF, end: QPointF) -> None:
        QObject.__init__(self, None)
        QGraphicsItem.__init__(self, None)

        assertRef(owner)
        assertRef(start)
        assertRef(end)

        self.owner = owner
        self.start: QPointF = start
        self.end: QPointF = end
        self.setZValue(self.depth_order)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = ...) -> None:
        """Draws the entire widget"""
        assertRef(self.startpin)
        assertRef(self.endpin)

        pen = QPen(Qt.green)
        pen.setWidth(3)
        painter.setPen(pen)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawLine(QLine(self.start, self.end))

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
