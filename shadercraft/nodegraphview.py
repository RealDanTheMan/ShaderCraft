from __future__ import annotations
import logging as Log
from PySide6.QtGui import QWheelEvent, QMouseEvent, QKeyEvent
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import QPointF, Qt, QPoint

from .asserts import assertRef, assertTrue
from .nodegraphscene import NodeGraphScene


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

        self.__scene: NodeGraphScene = None
        self._scale: float = 1.0
        self._scale_increment: float = 0.1

        self._pan_enabled: bool = False
        self._pan_ongoing: bool = False
        self._pan_mouse_pos: QPointF = QPointF()

    def setScene(self, scene: NodeGraphScene):
        """Bind graphics scene to this view"""
        self.__scene = scene
        super().setScene(scene)

    def wheelEvent(self, event: QWheelEvent) -> None:
        """
        Event invoked when mouse wheel is scrolled
        Zoom in/out of the graph every notch of the wheel movement.
        Zoom factor increment is consistent regardless of current zoom level.
        """
        factor: float = 1.0
        if event.angleDelta().y() > 0:
            # Zoom in graph viewport
            factor += (1.0 / self._scale) * self._scale_increment
        else:
            # Zoom out graph viewport
            factor -= (1.0 / self._scale) * self._scale_increment

        self.scale(factor, factor)
        self._scale *= factor

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Event handler invoken when a mouse button is pressed on top of the view"""
        if event.button() == Qt.MouseButton.RightButton:
            self.enableCameraPan(event.position())
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Event handler invoked when mouse button is release on top of the view"""
        if event.button() == Qt.MouseButton.RightButton and self._pan_enabled:
            self.disableCameraPan()
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Event handler invoked when mouse moves within the view"""
        if self._pan_enabled:
            self.doCameraPan(event.position())
            # Pan amount is dependant on zoom factor to ensure smooth and
            # responsive movement of the graph.
            mouse_delta = event.position() - self._pan_mouse_pos
            mouse_delta *= 1.0 / self._scale
            self.translate(mouse_delta.x(), mouse_delta.y())
            self._pan_mouse_pos = event.position()
            self._pan_ongoing = True
            return
        super().mouseMoveEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Event handler invoked when key is pressed while node graph is in focus"""
        if event.key() == Qt.Key_Delete and self.__scene is not None:
            Log.debug("Attempting to delete selected node")
            self.__scene.deleteSelectedNode()
            return
        super().keyPressEvent(event)

    def enableCameraPan(self, pos_origin: QPoint) -> None:
        """Enable mouse move event to pan the view of the graph"""
        assertRef(pos_origin)
        Log.debug("Enabling mouse pan mode")
        self._pan_enabled = True
        self._pan_mouse_pos = pos_origin

    def doCameraPan(self, mouse_pos: QPoint) -> None:
        """Pan the view of the graph based on delta between current and last mouse position"""
        self._pan_ongoing = True
        mouse_delta: QPoint = mouse_pos - self._pan_mouse_pos
        mouse_delta *= 1.0 / self._scale
        self.translate(mouse_delta.x(), mouse_delta.y())
        self._pan_mouse_pos = mouse_pos

    def disableCameraPan(self) -> None:
        """Disable mouse move events triggering view panning"""
        Log.debug("Disabling mouse pan mode")
        self._pan_enabled = False
        self._pan_ongoing = False
