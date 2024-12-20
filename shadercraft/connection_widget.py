from __future__ import annotations
from uuid import UUID, uuid1
from PySide6.QtCore import QObject, QRectF, QPointF, QLine, QPoint, Qt
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QPainter, QColor, QPen

from .node_widget import NodePin


class ConnectionWidget(QObject, QGraphicsItem):
    def __init__(self, startpin: NodePin, endpin: NodePin, uuid: UUID = uuid1()) -> None:
        QObject.__init__(self, None)
        QGraphicsItem.__init__(self, None)

        self.uuid: UUID = uuid
        self.startpin = startpin
        self.endpin = endpin

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = ...) -> None:
        """Draws the entire widget"""
        assert (self.startpin is not None)
        assert (self.endpin is not None)

        pen = QPen(Qt.green)
        pen.setWidth(4)
        painter.setPen(pen)
        
        line = QLine(self.startpin.scenePos().toPoint(), self.endpin.scenePos().toPoint())
        painter.drawLine(line)

    def boundingRect(self) -> QRectF:
        assert (self.startpin is not None)
        assert (self.endpin is not None)

        start = self.startpin.boundingRect()
        end = self.endpin.boundingRect()
        left = min(start.left(), end.left())
        right = max(start.right(), end.right())
        top = min(start.top(), end.top())
        bottom = max(start.bottom(), end.bottom())

        return QRectF(QPointF(left, top), QPointF(right, bottom))
