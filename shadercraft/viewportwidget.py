import logging as Log
import OpenGL.GL as GL
from PySide6.QtWidgets import QWidget
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QOpenGLContext
from PySide6.QtCore import QTimer

from .asserts import assertRef, assertTrue
import random


class ViewportWidget(QOpenGLWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        print(f"OpenGLWidget parent -> {self.parent()}")

    def initializeGL(self) -> None:
        """Initialise graphics context for this widget"""
        Log.info("Attempting to initialise OpenGL context")
        self.context().makeCurrent(self.context().surface())

    def paintGL(self) -> None:
        """Redraw GL surface"""
        self.makeCurrent()

        red: float = random.uniform(0.0, 1.0)
        green: float = random.uniform(0.0, 1.0)
        blue: float = random.uniform(0.0, 1.0)
        GL.glClearColor(red, green, blue, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

    def resizeGL(self, w: int, h: int) -> None:
        """
        Event handler invoked when the GL surface is resized.
        This can happen when the actual widget is resized by QT layout engine.
        """
        Log.debug("Resizing OpenGL viewport widget")
        GL.glViewport(0, 0, w, h)

    def requestRedraw(self) -> None:
        """Redraws the OpenGL viewport"""
        self.update()
