from typing import Optional
from dataclasses import dataclass
import os
import importlib.resources as res
import numpy as np
import OpenGL.GL as GL

from .asserts import assertRef, assertTrue, assertType

@dataclass
class GFXRenderable:
    vbo: GL.GLuint
    ebo: GL.GLuint
    vao: GL.GLuint
    vertices: list[float]
    indices: list[int]
    colors: list[float]
    normals: list[float]


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

        # Vertex Attribute Object
        vao: GL.GLuint = GL.glGenVertexArrays(1)
        assertTrue(vao != 0)
        GL.glBindVertexArray(vao)

        # Vertex indices buffer data
        ebo: GL.GLuint = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, ebo)
        GL.glBufferData(
            GL.GL_ELEMENT_ARRAY_BUFFER,
            len(renderable.indices),
            renderable.indices,
            GL.GL_STATIC_DRAW
        )

        vbo: GL.GLuint = GL.glGenBuffers(3)

        # Vertex position buffer data
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo[0])
        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            renderable.vertices.nbytes,
            renderable.vertices,
            GL.GL_STATIC_DRAW
        )

        # Vertex color buffer data
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo[1])
        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            renderable.colors.nbytes,
            renderable.colors,
            GL.GL_STATIC_DRAW
        )

        # Vertex normal buffer data
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo[2])
        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            renderable.normals.nbytes,
            renderable.normals,
            GL.GL_STATIC_DRAW
        )

        # Unbind all buffers
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

        renderable.vbo = vbo
        renderable.vao = vao
        renderable.ebo = ebo

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

        colors: np.array = np.array([
            1.0, 1.0, 1.0,
            1.0, 1.0, 1.0,
            1.0, 1.0, 1.0
        ], dtype=np.float32)

        normals: np.array = np.array([
            0.0, 0.0, 1.0,
            0.0, 0.0, 1.0,
            0.0, 0.0, 1.0
        ], dtype=np.float32)


        renderable: GFXRenderable = GFXRenderable(
            0,
            0,
            0,
            vertices,
            indices,
            colors,
            normals
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

        # Generate sphere vertex positions and normal vector
        vertices: list[float] = []
        normals: list[float] = []
        colors: list[float] = []
        for i in range(vsubdiv + 1):
            vangle: float = np.pi / 2 - i * (np.pi / vsubdiv)
            xy: float = np.cos(vangle)
            z: float = np.sin(vangle)

            for j in range(hsubdiv + 1):
                hangle: float = j * (2 * np.pi / hsubdiv)
                x: float = xy * np.cos(hangle)
                y: float = xy * np.sin(hangle)
                vertices.append([x, y, z])

                mag: float = np.sqrt(x*x + y*y + z*z)
                normals.append([x/mag, y/mag, z/mag])
                colors.append([1.0, 1.0, 1.0])

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
            0,
            np.array(vertices, dtype=np.float32),
            np.array(indices, dtype=np.uint32),
            np.array(colors, dtype=np.float32),
            np.array(normals, dtype=np.float32)
        )

        GFX.initRenderableBuffers(renderable)
        return renderable

    @staticmethod
    def bindRenderableShader(renderable: GFXRenderable, shader: GL.GLuint) -> None:
        """
        Binds renderable buffer data to given shader vertex attributes.

        Parameters:
            renderable (GFXRenderable) : Renderable structure with buffer data.
            shader (Gl.GLuint) : Compiled shader object handle.

        Returns:
            None
        """
        assertTrue(renderable.vbo is not None, "Invalid vertex buffer object")
        assertTrue(renderable.vao != 0, "Invalid vertex attribute object")
        assertTrue(renderable.ebo != 0, "Invalid element buffer object")
        assertRef(shader != 0)

        GL.glBindVertexArray(renderable.vao)

        # Vertex positon vertex attributes
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, renderable.vbo[0])
        layout_position: int = GL.glGetAttribLocation(shader, "position")
        assertTrue(layout_position != -1, "Failed to resolve 'position' vertex layout ID")
        GL.glVertexAttribPointer(
            layout_position,
            3,
            GL.GL_FLOAT,
            GL.GL_FALSE,
            3 * renderable.vertices.itemsize,
            None
        )
        GL.glEnableVertexAttribArray(layout_position)

        # Vertex color vertex attributes
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, renderable.vbo[1])
        layout_color: int = GL.glGetAttribLocation(shader, "color")
        assertTrue(layout_color != -1, "Failed to resolve 'color' vertex layout ID")
        GL.glVertexAttribPointer(
            layout_color,
            3,
            GL.GL_FLOAT,
            GL.GL_TRUE,
            3 * renderable.colors.itemsize,
            None
        )
        GL.glEnableVertexAttribArray(layout_color)

        # Vertex normal vertex attributes
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, renderable.vbo[2])
        layout_normal: int = GL.glGetAttribLocation(shader, "normal")
        assertTrue(layout_normal != -1, "Failed to resolve 'normal' vertex layout ID")
        GL.glVertexAttribPointer(
            layout_normal,
            3,
            GL.GL_FLOAT,
            GL.GL_TRUE,
            3 * renderable.normals.itemsize,
            None
        )
        GL.glEnableVertexAttribArray(layout_normal)

        GL.glBindVertexArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    @staticmethod
    def createFallbackShaderProgram() -> Optional[GL.GLuint]:
        """
        Creates minimalistic shader program which draws magenta solid color.
        """

        vs_src: str = res.files(r"shadercraft.resources.shaders").joinpath("fallback.vs")
        ps_src: str = res.files(r"shadercraft.resources.shaders").joinpath("fallback.ps")
        assertRef(vs_src)
        assertRef(ps_src)

        vs: GL.GLuint = GFX.compileShaderSourcefile(str(vs_src), GL.GL_VERTEX_SHADER)
        ps: GL.GLuint = GFX.compileShaderSourcefile(str(ps_src), GL.GL_FRAGMENT_SHADER,
                                                    console_output=True)
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
        assertType(console_output, bool)

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

    @staticmethod
    def compileShaderSourcefile(
            source_filepath: str,
            shader_type,
            log: str = None,
            console_output: bool = False
    ) -> Optional[GL.GLuint]:
        """
        Compiled given shader source file into shader object of given type.
        
        Paramters:
            source_filepath (str) : Filepath to the shader source file.
            shader_type : OpenGL shader type flag eg. GL.GL_VERTEX_SHADER.
            log (str) : out string containing compile Log, use None for no log.
            console_output (bool) : Pipe compile log to console output.

        Returns:
            (GL.GLuint) : OpenGL handle to compiled shader object, 0 if failed.
        """

        assertType(source_filepath, str)
        assertTrue(os.path.exists(source_filepath))
        assertType(shader_type, GL.constant.IntConstant)
        assertType(console_output, bool)

        with open(source_filepath, "r", encoding="utf-8") as file:
            src: str = file.read()
            return GFX.compileShaderSource(src, shader_type, log=log, console_output=console_output)

        return None
