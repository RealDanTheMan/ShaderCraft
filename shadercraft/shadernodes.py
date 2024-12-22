from __future__ import annotations
from uuid import UUID
from .node import Node, NodeConnection, NodeParameterValue, NodeValue, NodeInputOutput


class ShaderNodeBase(Node):
    def __init__(self) -> None:
        super().__init__()
        self._inputValues: dict[UUID, str] = {}

    def generateShaderCode(self) -> str:
        return ""


class FloatShaderNode(ShaderNodeBase):
    def __init__(self) -> None:
        super().__init__()
        self.name = "ShaderFloadNode"
        self.label = "Shader Float"
        self._output = self._addOutput("FloatOutput", "Float", NodeParameterValue.Float)
        self.default_val: float = 22.0

    def _generateOutput(self, node_output: NodeInputOutput) -> NodeValue:
        if node_output is self._output:
            return NodeValue(str, f"{self.name}_FloatOutput")
        return NodeValue.NoValue()

    def generateShaderCode(self) -> str:
        src: str = f"float  {self.name}_FloatOutput = {self.default_val}f;"
        return src


class MulShaderNode(ShaderNodeBase):
    def __init__(self) -> None:
        super().__init__()
        self.name = "MulNode"
        self.label = "Mul"
        self._inputA = self._addInput("MullInputA", "Value A", NodeParameterValue.Float)
        self._inputB = self._addInput("MullInputB", "Value B", NodeParameterValue.Float)
        self._output = self._addOutput("MulOutput", "Value", NodeParameterValue.Float)
        self._def_input_a = 1.0
        self._def_input_b = 1.0

    def _generateOutput(self, node_output: NodeInputOutput) -> NodeValue:
        if node_output is self._output:
            return NodeValue(str, f"{self.name}_MulOutput")
        return NodeValue.NoValue()

    def _generateInputValue(self, node_input: NodeInputOutput) -> NodeValue:
        if node_input is self._inputA:
            return NodeValue(str, f"{self._def_input_a}f")
        if node_input is self._inputB:
            return NodeValue(str, f"{self._def_input_b}f")

        return NodeValue.NoValue()

    def generateShaderCode(self) -> str:
        input_a = self.getNodeInputValue(self._inputA.uuid)
        input_b = self.getNodeInputValue(self._inputB.uuid)
        assert (input_a is not None)
        assert (input_b is not None)

        src: str = f"""
        float {self.name}_MulInputA = {input_a.value};
        float {self.name}_MulInputB = {input_b.value};
        float {self.name}_MulOutput = {self.name}_MulInputA * {self.name}_MulInputB;

        """
        return src

