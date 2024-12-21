from __future__ import annotations
from typing import Optional
from PySide6.QtGui import QWheelEvent, QMouseEvent, QWheelEvent
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import QPointF, Qt, QPointF


class NodeGraphView(QGraphicsView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.verticalScrollBar().disconnect(self)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.horizontalScrollBar().disconnect(self)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)

        self._scale: float = 1.0 
        self._scale_increment: float = 0.1
        self._pan_mode: bool = False
        self._pan_mouse_pos: QPointF = QPointF()

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Event invoked when mouse wheel is scrolled"""
        if event.angleDelta().y() > 0:
            # Zoom in graph viewport
            print("Zooming in")
            self.scale(1.0 + self._scale_increment, 1.0 + self._scale_increment)
        else:
            # Zoom out graph viewport
            print("Zooming out")
            self.scale(1.0 - self._scale_increment, 1.0 - self._scale_increment)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            print("Entering mouse panning mode")
            self._pan_mode = True
            self._pan_mouse_pos = event.position()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            print("Exiting mouse panning mode")
            self._pan_mode = False
        else:
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._pan_mode:
            mouse_delta = event.position() - self._pan_mouse_pos
            self.translate(mouse_delta.x(), mouse_delta.y())
            self._pan_mouse_pos = event.position()
            return
        else:
            super().mouseMoveEvent(event)
