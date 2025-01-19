from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from uuid import UUID
import textwrap

from .asserts import assertRef, assertType
from .node import Node, NodeValue, NodeIO


class ShaderValueHint(Enum):
    """
    Enum class denoting valid shader value types.

    """

    FLOAT = 0
    FLOAT2 = 1
    FLOAT3 = 2
    FLOAT4 = 4
    MAT3 = 5
    MAT4 = 6


@dataclass
class ShaderNodeIO(NodeIO):
    """
    Class representing shader node input/output properties.
    IO properties can form connections between shader nodes to produce shader logic.

    """

    def __init__(self, name: str, label: str, encoded_type: ShaderValueHint) -> None:
        super().__init__(name, label)

        assertType(encoded_type, ShaderValueHint)
        self.encoded_type: ShaderValueHint = encoded_type


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

    def canConnect(self, uuid: UUID, src_node: Node, src_uuid: UUID) -> bool:
        """
        Moderates connection requests to this shader node.
        For the time being we only accept connections of matchin shader value type:
            Good: FLOAT <-> FLOAT
            Good: FLOAT3 <-> FLOAT3
            Bad: FLOAT3 <-> FLOAT
        """
        io0: ShaderNodeIO = self.getNodeInput(uuid)
        io1: ShaderNodeIO = src_node.getNodeOutput(src_uuid)
        assertRef(io0)
        assertRef(io1)

        # Only accept IO connections if they are of ShaderNodeIO type
        if isinstance(io0, ShaderNodeIO) and isinstance(io1, ShaderNodeIO):
            if io0.encoded_type == io1.encoded_type:
                return True

        return False


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
        self.def_albedo: list[float] = [1.0, 1.0, 1.0]
        self.def_alpha: float = 1.0

        # Node input properties
        self.albedo_input = ShaderNodeIO("Albedo", "Albedo", ShaderValueHint.FLOAT3)
        self._registerInput(self.albedo_input)

        self.alpha_input = ShaderNodeIO("Alpha", "Alpha", ShaderValueHint.FLOAT)
        self._registerInput(self.alpha_input)

    def _generateInputValue(self, node_input: NodeIO) -> NodeValue:
        """
        Generate static default values for any input if not connected to any other ndoes.
        """
        if node_input is self.albedo_input:
            x: float = self.def_albedo[0]
            y: float = self.def_albedo[1]
            z: float = self.def_albedo[2]
            return NodeValue(str, f"vec3({x}, {y}, {z})")
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
        vec3 albedo = {albedo_value.value};
        float alpha = {alpha_value.value};
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
        self.default_input_val: float = 1.0

        self.float_input = ShaderNodeIO("FloatInput", "In", ShaderValueHint.FLOAT)
        self._registerInput(self.float_input)

        self.float_output = ShaderNodeIO("FloatOutput", "Out", ShaderValueHint.FLOAT)
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
        self.input_a = ShaderNodeIO("MulInputA", "A", ShaderValueHint.FLOAT)
        self._registerInput(self.input_a)
        self.input_b = ShaderNodeIO("MulInputB", "B", ShaderValueHint.FLOAT)
        self._registerInput(self.input_b)

        # Node output
        self.float_output = ShaderNodeIO("MulOutput", "Value", ShaderValueHint.FLOAT)
        self._registerOutput(self.float_output)

    def _generateOutput(self, node_output: NodeIO) -> NodeValue:
        if node_output is self.float_output:
            return NodeValue(str, f"{self.name}_{self.float_output.name}")
        return NodeValue.noValue()

    def _generateInputValue(self, node_input: NodeIO) -> NodeValue:
        if node_input is self.input_a:
            return NodeValue(str, f"{self._def_input_a}")
        if node_input is self.input_b:
            return NodeValue(str, f"{self._def_input_b}")

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

class MakeVec3Node(ShaderNodeBase):
    """
    MakeVec3 shader node creates any vec3 value from 3 given float inputs.
    """

    label = "MakeVec3"

    def __init__(self) -> None:
        super().__init__()
        self.name = "MakeVec3Node"
        self.label = "Vec3"

        # Default input fallback values
        self._def_x: float = 0.0
        self._def_y: float = 0.0
        self._def_z: float = 0.0

        # Node Inputs
        self.input_x: ShaderNodeIO = ShaderNodeIO("Vec3InputX", "X", ShaderValueHint.FLOAT)
        self.input_y: ShaderNodeIO = ShaderNodeIO("Vec3InputX", "Y", ShaderValueHint.FLOAT)
        self.input_z: ShaderNodeIO = ShaderNodeIO("Vec3InputX", "Z", ShaderValueHint.FLOAT)
        self._registerInput(self.input_x)
        self._registerInput(self.input_y)
        self._registerInput(self.input_z)

        # Node Outputs
        self.output: ShaderNodeIO = ShaderNodeIO("Vec3Output", "Vec3", ShaderValueHint.FLOAT3)
        self._registerOutput(self.output)

    def _generateInputValue(self, node_input: NodeIO) -> NodeValue:
        """
        Generate default input value if no connections are form to given input property.
        """

        if node_input is self.input_x:
            return NodeValue(str, f"{self._def_x}")
        if node_input is self.input_y:
            return NodeValue(str, f"{self._def_y}")
        if node_input is self.input_z:
            return NodeValue(str, f"{self._def_z}")

        return NodeValue.noValue()

    def _generateOutput(self, node_output: NodeIO) -> NodeValue:
        """
        Generates vec3 output value shader reference.
        """
        if node_output is self.output:
            return NodeValue(str, f"{self.name}_{self.output.name}")

        return NodeValue.noValue()

    def generateShaderCode(self) -> str:
        """
        Generate GLSL shader source code for this node.
        """

        x: NodeValue = self.getNodeInputValue(self.input_x.uuid)
        y: NodeValue = self.getNodeInputValue(self.input_x.uuid)
        z: NodeValue = self.getNodeInputValue(self.input_z.uuid)
        assertRef(x)
        assertRef(y)
        assertRef(z)

        output: NodeValue = self.getNodeOutputValue(self.output.uuid)
        assertRef(output)
        src: str = f"""
                vec3 {output.value} = vec3({x.value}, {y.value}, {z.value});
        """

        return textwrap.dedent(src).strip()
