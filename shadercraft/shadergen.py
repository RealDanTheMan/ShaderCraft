from __future__ import annotations
from typing import Optional
import importlib.resources as res
from string import Template as StringTemplate
import os
from pathlib import Path
import logging as Log
import textwrap

from .asserts import assertRef, assertTrue, assertType
from .shadernodes import ShaderNodeBase, OutputShaderNode

class ShaderGen(object):
    def __init__(self) -> None:
        self.vs_source: str = ""
        self.ps_source: str = ""
        self.vertex_shader: str = None
        self.pixel_shader: str = None

    def _generateVertexShader(self) -> str:
        """
        Generate vertex shader source code.
        """

        # For the time being vertex shader is static data not influenced by shader nodes.
        # This means we can simply load template file and return contents.
        template: str = res.files(r"shadercraft.resources.shaders").joinpath("template_standard.vs")
        assertTrue(os.path.exists(template), "Failed to locate vertex shader template file")

        src: str = None
        with open(template, "r", encoding="utf-8") as file:
            src = file.read()

        assertRef(src, "Failed to read vertex shader template file")
        return src

    def _generatePixelShader(self, nodes: list[ShaderNodeBase]) -> str:
        """
        Generate shader source grom given node.
        The logic serialised from node is wrapped in interpretGraph() function.

        Parameters:
            nodes (list[ShaderNodeBase]) : graph nodes - must contain one OutputShaderNode

        Returns:
            str : Shader source code
        """

        # Find OutputShader node.
        output_node: OutputShaderNode = None
        for node in nodes:
            if isinstance(node, OutputShaderNode):
                output_node = node
                break

        # Resolve all descendant nodes connectin to output node.
        assertRef(output_node, "Cannot find OuputShaderNode")
        logic_nodes: list[ShaderNodeBase] = output_node.getDownstreamNodes()

        # Serialise shader code along with debug summary text.
        src_items: list[str] = []
        for node in logic_nodes:
            assertType(node, ShaderNodeBase)
            summary: str = node.generateShaderCodeSummary()
            code: str = node.generateShaderCode()
            src_items.append(summary)
            src_items.append("\n")
            src_items.append(code)
            src_items.append("\n\n")

        # Load template pixel shader file and inject node generated code.
        node_src: str = "".join(src_items)
        node_src = textwrap.indent(node_src, "    ")
        template: str = res.files(r"shadercraft.resources.shaders").joinpath("template_standard.ps")
        assertTrue(os.path.exists(template), "Failed to locate pixel shader template file")
        src: str = None
        with open(template, "r", encoding="utf-8") as file:
            src = file.read()

        assertRef(src, "Failed to read pixel shader template file")
        src_template: StringTemplate = StringTemplate(src)
        final_src: str = src_template.substitute(graph_src=node_src)

        return final_src

    def generateSource(self, nodes: list[ShaderNodeBase]) -> None:
        """
        Generates shader sources based on the given list of shader node.
        List of shader nodes must contain OutputShaderNode

        Parameters:
            nodes (list[ShaderNodeBase]) : List of shader nodes to build source from.
        """
        assertTrue(len(nodes) > 0)

        Log.info("Generating shader sources...")
        self.vs_source = self._generateVertexShader()
        self.ps_source = self._generatePixelShader(nodes)
        assertRef(self.vs_source)
        assertRef(self.ps_source)

    def writeSource(self, output_dir: str) -> None:
        """
        Writes generated shader sources to disk
        """

        assertRef(self.vs_source)
        assertRef(self.ps_source)

        assertType(output_dir, str)
        os.makedirs(output_dir, exist_ok=True)

        self.vertex_shader = str(Path(output_dir).resolve().joinpath("gen_shader.vs"))
        self.pixel_shader= str(Path(output_dir).resolve().joinpath("gen_shader.ps"))

        Log.debug(f"Serialising vertex shader -> {self.vertex_shader}")
        with open(self.vertex_shader, "w", encoding="utf-8") as file:
            file.write(self.vs_source)

        Log.debug(f"Serialising pixel shader -> {self.pixel_shader}")
        with open(self.pixel_shader, "w", encoding="utf-8") as file:
            file.write(self.ps_source)
