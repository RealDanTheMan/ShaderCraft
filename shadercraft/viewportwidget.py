import logging as Log
import moderngl as GL
from PySide6.QtWidgets import QWidget
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QOpenGLContext
from PySide6.QtCore import QTimer

from .asserts import assertRef, assertTrue


class ViewportWidget(QOpenGLWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        print(f"OpenGLWidget parent -> {self.parent()}")
        self.ctx: GL.Context = None

    def initializeGL(self) -> None:
        """Initialise graphics context for this widget"""
        assertTrue(self.ctx is None, "Graphics context already initialised")
        Log.info("Attempting to initialise OpenGL context")
        self.ctx = GL.create_context()
        self.ctx.screen.use()
        self.ctx.clear(0.0, 1.0, 0.0, 1.0)

    def paintGL(self) -> None:
        """Redraw GL surface"""
        assertRef(self.ctx)
        self.makeCurrent()
        self.ctx.clear(1.0, 0.0, 1.0, 1.0)
        QOpenGLContext.currentContext().functions().glClearColor(1.0, 0.0, 0.0, 1.0)
        QOpenGLContext.currentContext().functions().glClear(1)

    def resizeGL(self, w: int, h: int) -> None:
        """
        Event handler invoked when the GL surface is resized.
        This can happen when the actual widget is resized by QT layout engine.
        """
        assertRef(self.ctx)
        Log.debug("Resizing OpenGL viewport widget")
        self.ctx.viewport = (0, 0, w, h)

    def requestRedraw(self) -> None:
        """Redraws the OpenGL viewport"""
        self.update()
