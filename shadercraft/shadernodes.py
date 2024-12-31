from __future__ import annotations
import textwrap

from .asserts import assertRef
from .node import Node, NodeValue, NodeIO


class ShaderNodeBase(Node):
    """
    Base class for all shader nodes.
    Shader nodes are graph nodes that can be connected together to generate
    shader code used to compile shaders.
    """
    label = "Shader Node"

    def __init__(self) -> None:
        super().__init__()

    def generateShaderCode(self) -> str:
        """
        Get node generated shader code in a string form.

        Every shader node type must implement this method.
        """
        return ""

    def generateShaderCodeSummary(self) -> str:
        """
        Get summary for this shader node in a comment block format.
        """
        summary: str = f"""
        /// -------------------------------------------------------------------
        /// Node Class: {type(self)}
        /// Node Label: {self.label}
        /// Node Name: {self.name}
        /// Node UUID: {self.uuid}
        ///--------------------------------------------------------------------
        """
        return textwrap.dedent(summary).strip()


class OutputShaderNode(ShaderNodeBase):
    """
    Output shader node is the final node in the graph tree.
    Final shader code for current graph is generated from this node and
    any nodes down stream from this node.
    """
    label = "Output"

    def __init__(self):
        super().__init__()
        self.name = "OutputNode"

        # Default input values
        self.def_albedo = 1.0
        self.def_alpha = 1.0

        # Node input properties
        self.albedo_input = NodeIO.create("Albedo", "Albedo")
        self._registerInput(self.albedo_input)

        self.alpha_input = NodeIO.create("Alpha", "Alpha")
        self._registerInput(self.alpha_input)

    def _generateInputValue(self, node_input: NodeIO) -> NodeValue:
        if node_input is self.albedo_input:
            return NodeValue(str, f"{self.def_albedo}")
        if node_input is self.alpha_input:
            return NodeValue(str, f"{self.def_alpha}")
        return NodeValue.noValue()

    def generateShaderCode(self) -> str:
        """Generate shader code for this node"""
        albedo_value: NodeValue = self.getNodeInputValue(self.albedo_input.uuid)
        alpha_value: NodeValue = self.getNodeInputValue(self.alpha_input.uuid)
        assertRef(albedo_value)
        assertRef(alpha_value)

        src: str = f"""
        float albedo = {albedo_value.value}
        float alpha = {alpha_value.value}
        """

        return textwrap.dedent(src).strip()


class FloatShaderNode(ShaderNodeBase):
    """
    Float shader is a simple node that defines shader float variable.
    """
    label = "Float"

    def __init__(self) -> None:
        super().__init__()
        self.name = "ShaderFloadNode"
        self.label = "Shader Float"
        self.default_input_val: float = 0.0

        self.float_input = NodeIO.create("FloatInput", "Float In")
        self._registerInput(self.float_input)

        self.float_output = NodeIO.create("FloatOutput", "Float Out")
        self._registerOutput(self.float_output)

    def _generateInputValue(self, node_input: NodeIO) -> NodeValue:
        """Generate default input value for non connected inputs"""
        if node_input is self.float_input:
            return NodeValue(str, f"{self.default_input_val}")
        return NodeValue.noValue()

    def _generateOutput(self, node_output: NodeIO) -> NodeValue:
        """Generate value for given node output property"""
        if node_output is self.float_output:
            return NodeValue(str, f"{self.name}_{self.float_output.name}")
        return NodeValue.noValue()

    def generateShaderCode(self) -> str:
        """Generates float node shader code"""
        input_val = self.getNodeInputValue(self.float_input.uuid)
        assertRef(input_val)

        src: str = f"float  {self.name}_{self.float_output.name} = {input_val.value}f;"
        return src.strip()



class MulShaderNode(ShaderNodeBase):
    """
    Mull shader node performs multiplication of two input values and outputs result.
    """
    label = "Mul"

    def __init__(self) -> None:
        super().__init__()
        self.name = "MulNode"
        self.label = "Mul"

        # Default input values
        self._def_input_a = 1.0
        self._def_input_b = 1.0

        # Node inputs
        self.input_a = NodeIO.create("MulInputA", "Value A")
        self._registerInput(self.input_a)
        self.input_b = NodeIO.create("MulInputB", "Value B")
        self._registerInput(self.input_b)

        # Node output
        self.float_output = NodeIO.create("MulOutput", "Value")
        self._registerOutput(self.float_output)

    def _generateOutput(self, node_output: NodeIO) -> NodeValue:
        if node_output is self.float_output:
            return NodeValue(str, f"{self.name}_{self.float_output.name}")
        return NodeValue.noValue()

    def _generateInputValue(self, node_input: NodeIO) -> NodeValue:
        if node_input is self.input_a:
            return NodeValue(str, f"{self._def_input_a}f")
        if node_input is self.input_b:
            return NodeValue(str, f"{self._def_input_b}f")

        return NodeValue.noValue()

    def generateShaderCode(self) -> str:
        val_a = self.getNodeInputValue(self.input_a.uuid)
        val_b = self.getNodeInputValue(self.input_b.uuid)

        assertRef(val_a)
        assertRef(val_b)

        src: str = f"""
        float {self.input_a.name} = {val_a.value};
        float {self.input_b.name} = {val_b.value};
        float {self.name}_{self.float_output.name} = {self.input_a.name} * {self.input_b.name};

        """
        return textwrap.dedent(src).strip()
