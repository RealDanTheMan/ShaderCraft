from __future__ import annotations
from uuid import UUID

from .asserts import assertRef
from .node import Node, NodeParameterValue, NodeValue, NodeInputOutput


class ShaderNodeBase(Node):
    """
    Base class for all shader nodes.
    Shader nodes are graph nodes that can be connected together to generate
    shader code used to compile shaders.
    """

    def __init__(self) -> None:
        super().__init__()

    def generateShaderCode(self) -> str:
        """
        Get node generated shader code in a string form.

        Every shader node type must implement this method.
        """
        return ""


class FloatShaderNode(ShaderNodeBase):
    """
    Float shader is a simple node that defines shader float variable.
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "ShaderFloadNode"
        self.label = "Shader Float"
        self.default_input_val: float = 0.0

        self.float_input = NodeInputOutput.create("FloatInput", "Float In", NodeParameterValue.FLOAT)
        self._registerInput(self.float_input)

        self.float_output = NodeInputOutput.create("FloatOutput", "Float Out", NodeParameterValue.FLOAT)
        self._registerOutput(self.float_output)

    def _generateInputValue(self, node_input: NodeInputOutput) -> NodeValue:
        """Generate default input value for non connected inputs"""
        if node_input is self.float_input:
            return NodeValue(str, f"{self.default_input_val}")
        return NodeValue.noValue()

    def _generateOutput(self, node_output: NodeInputOutput) -> NodeValue:
        """Generate value for given node output property"""
        if node_output is self.float_output:
            return NodeValue(str, f"{self.name}_{self.float_output.name}")
        return NodeValue.noValue()

    def generateShaderCode(self) -> str:
        """Generates float node shader code"""
        input_val = self.getNodeInputValue(self.float_input.uuid)
        assertRef(input_val)

        src: str = f"float  {self.name}_{self.float_output.name} = {input_val.value}f;"
        return src


class MulShaderNode(ShaderNodeBase):
    """
    Mull shader node performs multiplication of two input values and outputs result.
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "MulNode"
        self.label = "Mul"

        # Default input values
        self._def_input_a = 1.0
        self._def_input_b = 1.0

        # Node inputs
        self.input_a = NodeInputOutput.create("MulInputA", "Value A", NodeParameterValue.FLOAT)
        self._registerInput(self.input_a)
        self.input_b = NodeInputOutput.create("MulInputB", "Value B", NodeParameterValue.FLOAT)
        self._registerInput(self.input_b)

        # Node output
        self.float_output = NodeInputOutput.create("MulOutput", "Value", NodeParameterValue.FLOAT)
        self._registerOutput(self.float_output)

    def _generateOutput(self, node_output: NodeInputOutput) -> NodeValue:
        if node_output is self.float_output:
            return NodeValue(str, f"{self.name}_{self.float_output.name}")
        return NodeValue.noValue()

    def _generateInputValue(self, node_input: NodeInputOutput) -> NodeValue:
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
        return src

