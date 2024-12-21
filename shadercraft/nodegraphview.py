from __future__ import annotations
from typing import Optional
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QGraphicsView


class NodeGraphView(QGraphicsView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._scale: float = 1.0 
        self._scale_increment = 0.1

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Event invoked when mouse wheel is scrolled"""
        if event.angleDelta().y() > 0:
            # Zoom in graph viewport
            self.scale(1.0 + self._scale_increment, 1.0 + self._scale_increment)
        else:
            # Zoom out graph viewport
            self.scale(1.0 - self._scale_increment, 1.0 - self._scale_increment)
