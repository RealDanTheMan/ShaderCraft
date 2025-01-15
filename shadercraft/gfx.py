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
    indices: list[int]


class GFX:
    """
    Utility class for creating various data for OpenGL viewport widget.
    """

    @staticmethod
    def initRenderableBuffers(renderable: GFXRenderable) -> None:
        """
        Initialises OpenGL buffers of given renderable data.

        Parameters:
            renderable (GFXRenderable) : Renderable structure to initialise buffers from.

        Returns:
            None
        """
        vao: GL.GLuint = GL.glGenVertexArrays(1)
        assertTrue(vao != 0)
        GL.glBindVertexArray(vao)

        vbo: GL.GLuint = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            renderable.vertices.nbytes,
            renderable.vertices,
            GL.GL_STATIC_DRAW
        )

        # Unbind all buffers
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        renderable.vbo = vbo
        renderable.vao = vao

    @staticmethod
    def createTriangleRenderable() -> GFXRenderable:
        vertices: np.array = np.array([
            -0.5, -0.5, 0.0,
            0.5, -0.5, 0.0,
            0.0, 0.5, 0.0
        ], dtype=np.float32)

        indices: np.array = np.array([
            0,
            1,
            2
        ], dtype=np.uint32)


        renderable: GFXRenderable = GFXRenderable(
            0,
            0,
            vertices,
            indices
        )

        GFX.initRenderableBuffers(renderable)
        return renderable

    @staticmethod
    def createSphereRenderable(radius: float, vsubdiv: int, hsubdiv: int) -> GFXRenderable:
        """
        Generate renderable geometry of a sphere.

        Parameters:
            radius (float): Sphere radius.
            vsubdiv (int): Number of vertecal subdivisions.
            hsubdiv (int): Number of horizontal subdivisions.

        Returns:
            Renderable (GFXRenderable): Renderable structure containing sphere geometry
        """

        # Generate sphere vertex positions
        vertices: list[float] = []
        for i in range(vsubdiv + 1):
            vangle: float = np.pi / 2 - i * (np.pi / vsubdiv)
            xy: float = np.cos(vangle)
            z: float = np.sin(vangle)

            for j in range(hsubdiv + 1):
                hangle: float = j * (2 * np.pi / hsubdiv)
                x: float = xy * np.cos(hangle)
                y: float = xy * np.sin(hangle)
                vertices.append([x, y, z])

        # Generate sphere vertex indices
        indices: list[int] = []
        for i in range(vsubdiv):
            for j in range(hsubdiv):
                t0: int = i * (hsubdiv + 1) + j
                t1: int = t0 + hsubdiv + 1

                # First triangle of sphere quad at given subdivision
                indices.append(t0)
                indices.append(t1)
                indices.append(t0 + 1)

                # Second triangle of sphere quad at given subdivision
                indices.append(t1)
                indices.append(t1 + 1)
                indices.append(t0 + 1)

        renderable: GFXRenderable = GFXRenderable(
            0,
            0,
            np.array(vertices, dtype=np.float32),
            np.array(indices, dtype=np.uint32)
        )

        GFX.initRenderableBuffers(renderable)
        return renderable

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
