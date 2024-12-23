from __future__ import annotations
from PySide6.QtGui import QWheelEvent, QMouseEvent
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import QPointF, Qt


class NodeGraphView(QGraphicsView):
    """
    Class that represents the actual view of the node graph scene, its
    responsible for draw ing the actual nodes and other items on the graph.
    """

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
        """Event handler invoken when a mouse button is pressed on top of the view"""
        if event.button() == Qt.MouseButton.RightButton:
            print("Entering mouse panning mode")
            self._pan_mode = True
            self._pan_mouse_pos = event.position()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Event handler invoked when mouse button is release on top of the view"""
        if event.button() == Qt.MouseButton.RightButton:
            print("Exiting mouse panning mode")
            self._pan_mode = False
        else:
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Event handler invoked when mouse moves within the view"""
        if self._pan_mode:
            mouse_delta = event.position() - self._pan_mouse_pos
            self.translate(mouse_delta.x(), mouse_delta.y())
            self._pan_mouse_pos = event.position()
            return
        super().mouseMoveEvent(event)
