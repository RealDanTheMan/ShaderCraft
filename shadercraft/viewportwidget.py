import os
import ctypes
import logging as Log
import OpenGL.GL as GL
from PySide6.QtWidgets import QWidget
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QOpenGLContext
from PySide6.QtCore import QTimer

from .asserts import assertRef, assertTrue, assertType
from .gfx import GFX, GFXRenderable


class ViewportWidget(QOpenGLWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.fallback_shader: GL.GLuint = None
        self.active_shader: GL.GLuint = None
        self.preview_geo: GFXRenderable = None

    def initializeGL(self) -> None:
        """Initialise graphics context for this widget"""
        Log.info("Attempting to initialise OpenGL context")
        Log.info(f"OpenGL Version: {GL.glGetString(GL.GL_VERSION).decode()}")
        self.context().makeCurrent(self.context().surface())
        self.fallback_shader = GFX.createFallbackShaderProgram()
        self.active_shader = self.fallback_shader
        self.preview_geo = GFX.createSphereRenderable(1, 64, 64)
        GFX.bindRenderableShader(self.preview_geo, self.active_shader)

        # Enable OpenGL debug logging
        # TODO: We should drive this using app settings
        Log.info("Enabling OpenGL debug logging")
        GL.glEnable(GL.GL_DEBUG_OUTPUT)
        GL.glEnable(GL.GL_DEBUG_OUTPUT_SYNCHRONOUS)
        #GL.glDebugMessageCallback(GL.GLDEBUGPROC(self.graphicsMessageCallback), None)

    def paintGL(self) -> None:
        """Redraw GL surface"""
        self.makeCurrent()

        # Clear render target
        GL.glClearColor(0.33, 0.33, 0.33, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Bind geometry buffers and shader
        GL.glBindVertexArray(self.preview_geo.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.preview_geo.vbo[0])
        GL.glUseProgram(self.active_shader)
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

    def requestShader(self, vs: str, ps: str) -> bool:
        """
        Attempts to load and bind new shader for the preview goemetry.

        Parameters:
            vs (str) : Filepath to vertex shader file.
            ps (str) : Filepath to pixel shader file.

        Returns:
            bool : True of shader load and compile succeded, False otherwise.
        """

        assertType(vs, str)
        assertType(ps, str)
        assertTrue(os.path.exists(vs))
        assertTrue(os.path.exists(ps))

        self.makeCurrent()
        shader: GL.GLuint = GFX.createShaderFromFiles(vs, ps)
        if shader == 0:
            Log.warning("Failed to load or compile shade source files")
            self.active_shader = self.fallback_shader
            return False

        self.active_shader = shader

        GFX.bindRenderableShader(self.preview_geo, self.active_shader)
        return True

    @staticmethod
    def graphicsMessageCallback(
            src,
            msg_type,
            msg_id,
            severity,
            msg_len,
            msg,
            user_param
    ) -> None:
        """
        Event handler invoked when OpenGL generates debug output message.
        Debug logging has to be enabled first.
        """
        Log.debug("Received graphics log message!")

        message: str = ctypes.cast(msg, ctypes.POINTER(ctypes.c_char)).value.decode("utf-8")
        print(message)

        log_msg: str = f"""
        OpenGL Debug Message:
            Source {src}
            Type: {msg_type}
            ID: {msg_id}
            Severity: {severity}
            Message: {message}
        """

        Log.debug(log_msg)
