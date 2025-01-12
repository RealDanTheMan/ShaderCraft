from typing import Optional
from dataclasses import dataclass
import numpy as np
import OpenGL.GL as GL

from .asserts import assertRef, assertTrue, assertType

@dataclass
class GFXRenderable:
    vbo: GL.GLuint
    vao: GL.GLuint
    vertices: list[float]


class GFX:
    """
    Utility class for creating various data for OpenGL viewport widget.
    """

    @staticmethod
    def createTriangleRenderable() -> GFXRenderable:
        vertices: np.array = np.array([
            -0.5, -0.5, 0.0,
            0.5, -0.5, 0.0,
            0.0, 0.5, 0.0
        ], dtype=np.float32)

        vao: GL.GLuint = GL.glGenVertexArrays(1)
        assertTrue(vao != 0)
        GL.glBindVertexArray(vao)

        vbo: GL.GLuint = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_STATIC_DRAW)

        # Unbind all buffers
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        return GFXRenderable(
            vbo,
            vao,
            vertices
        )

    @staticmethod
    def bindRenderableShader(renderable: GFXRenderable, shader: GL.GLuint) -> None:
        assertTrue(renderable.vbo != 0)
        assertTrue(renderable.vao != 0)
        assertRef(shader != 0)

        GL.glBindVertexArray(renderable.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, renderable.vbo)
        layout_position: int = GL.glGetAttribLocation(shader, "position")
        GL.glVertexAttribPointer(
            layout_position,
            3,
            GL.GL_FLOAT,
            GL.GL_FALSE,
            3 * renderable.vertices.itemsize,
            None
        )

        GL.glEnableVertexAttribArray(layout_position)
        GL.glBindVertexArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    @staticmethod
    def createFallbackShaderProgram() -> Optional[GL.GLuint]:
        """
        Creates minimalistic shader program which draws magenta solid color.
        """

        vs_src: str = """
        #version 330 core
        layout (location = 0) in vec3 position;
        
        void main() 
        {
            gl_Position = vec4(position, 1.0);
        }
        """

        ps_src: str = """
        #version 330 core

        out vec4 frag_color;
        void main() 
        {
            frag_color = vec4(1.0, 0.0, 1.0, 1.0);
        }
        """

        vs: GL.GLuint = GFX.compileShaderSource(vs_src, GL.GL_VERTEX_SHADER)
        ps: GL.GLuint = GFX.compileShaderSource(ps_src, GL.GL_FRAGMENT_SHADER)
        assertRef(vs, "Failed to compile fallback vertex shader")
        assertRef(ps, "Failed to compile fallback pixel shader")

        program: GL.GLuint = GL.glCreateProgram()
        assertRef(program, "Failed to initialise OpenGL shader program")

        GL.glAttachShader(program, vs)
        GL.glAttachShader(program, ps)
        GL.glLinkProgram(program)

        GL.glDeleteShader(vs)
        GL.glDeleteShader(ps)

        return program

    @staticmethod
    def compileShaderSource(
            source: str,
            shader_type,
            log: str = None,
            console_output: bool = False
    ) -> Optional[GL.GLuint]:
        """
        Compile given shader source into shader object of given type
        Returns None if compilation failed.
        """
        assertType(source, str)
        assertType(shader_type, GL.constant.IntConstant)
        assertTrue(shader_type == GL.GL_VERTEX_SHADER or shader_type == GL.GL_FRAGMENT_SHADER)

        shader: GL.GLuint = GL.glCreateShader(shader_type)
        assertTrue(shader != 0, "Failed to create fallback shader object")
        GL.glShaderSource(shader, source)
        GL.glCompileShader(shader)

        if log is not None:
            log = GL.glGetShaderInfoLog(shader)

        if console_output:
            print(f"{GL.glGetShaderInfoLog(shader)}")

        if GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS):
            return shader
        return None
