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
        self.default_input_val: float = 0.0

        self.floatInput = NodeInputOutput.create("FloatInput", "Float In", NodeParameterValue.FLOAT)
        self._registerInput(self.floatInput)

        self.floatOutput = NodeInputOutput.create("FloatOutput", "Float Out", NodeParameterValue.FLOAT)
        self._registerOutput(self.floatOutput)

    def _generateInputValue(self, node_input: NodeInputOutput) -> NodeValue:
        if node_input is self.floatInput:
            return NodeValue(str, f"{self.default_input_val}")
        else:
            return NodeValue.noValue()

    def _generateOutput(self, node_output: NodeInputOutput) -> NodeValue:
        if node_output is self.floatOutput:
            return NodeValue(str, f"{self.name}_{self.floatOutput.name}")
        return NodeValue.noValue()

    def generateShaderCode(self) -> str:
        input_val = self.getNodeInputValue(self.floatInput.uuid)
        assert (input_val is not None)

        src: str = f"float  {self.name}_{self.floatOutput.name} = {input_val.value}f;"
        return src


class MulShaderNode(ShaderNodeBase):
    def __init__(self) -> None:
        super().__init__()
        self.name = "MulNode"
        self.label = "Mul"
        
        # Default input values
        self._def_input_a = 1.0
        self._def_input_b = 1.0
        
        # Node inputs
        self.inputA = NodeInputOutput.create("MulInputA", "Value A", NodeParameterValue.FLOAT)
        self._registerInput(self.inputA)
        self.inputB = NodeInputOutput.create("MulInputB", "Value B", NodeParameterValue.FLOAT)
        self._registerInput(self.inputB)
        
        # Node output
        self.floatOutput = NodeInputOutput.create("MulOutput", "Value", NodeParameterValue.FLOAT)
        self._registerOutput(self.floatOutput)

    def _generateOutput(self, node_output: NodeInputOutput) -> NodeValue:
        if node_output is self.floatOutput:
            return NodeValue(str, f"{self.name}_{self.floatOutput.name}")
        return NodeValue.noValue()

    def _generateInputValue(self, node_input: NodeInputOutput) -> NodeValue:
        if node_input is self.inputA:
            return NodeValue(str, f"{self._def_input_a}f")
        if node_input is self.inputB:
            return NodeValue(str, f"{self._def_input_b}f")

        return NodeValue.noValue()

    def generateShaderCode(self) -> str:
        input_a = self.getNodeInputValue(self.inputA.uuid)
        input_b = self.getNodeInputValue(self.inputB.uuid)
        assert (input_a is not None)
        assert (input_b is not None)

        src: str = f"""
        float {self.inputA.name} = {input_a.value};
        float {self.inputB.name} = {input_b.value};
        float {self.name}_{self.floatOutput.name} = {self.inputA.name} * {self.inputB.name};

        """
        return src

