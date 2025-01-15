import logging as Log
import OpenGL.GL as GL
from PySide6.QtWidgets import QWidget
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QOpenGLContext
from PySide6.QtCore import QTimer

from .asserts import assertRef, assertTrue
from .gfx import GFX, GFXRenderable


class ViewportWidget(QOpenGLWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.fallback_shader: GL.GLuint = None
        self.preview_geo: GFXRenderable = None

    def initializeGL(self) -> None:
        """Initialise graphics context for this widget"""
        Log.info("Attempting to initialise OpenGL context")
        Log.info(f"OpenGL Version: {GL.glGetString(GL.GL_VERSION).decode()}")
        self.context().makeCurrent(self.context().surface())
        self.fallback_shader = GFX.createFallbackShaderProgram()
        self.preview_geo = GFX.createSphereRenderable(1, 64, 64)
        GFX.bindRenderableShader(self.preview_geo, self.fallback_shader)

    def paintGL(self) -> None:
        """Redraw GL surface"""
        self.makeCurrent()

        # Clear render target
        GL.glClearColor(0.33, 0.33, 0.33, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Bind geometry buffers and shader
        GL.glBindVertexArray(self.preview_geo.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.preview_geo.vbo)
        GL.glUseProgram(self.fallback_shader)
        GL.glBindVertexArray(self.preview_geo.vao)

        # Draw
        GL.glDrawElements(
            GL.GL_TRIANGLES,
            len(self.preview_geo.indices),
            GL.GL_UNSIGNED_INT,
            self.preview_geo.indices
        )

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
