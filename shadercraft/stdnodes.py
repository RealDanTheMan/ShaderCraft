from .node import Node, NodeParameterValue


class FloatNode(Node):
    def __init__(self):
        super().__init__()

        self.name = "Float Node"
        self.label = "Float"
        self._addOutput("Float Output", "Float", NodeParameterValue.Float)


class MulNode(Node):
    def __init__(self):
        super().__init__()
        self.name = "Multiplication Node"
        self.label = "Mul"
        self._addInput("Mul Input A", "Value A", NodeParameterValue.Float)
        self._addInput("Mul Input B", "Value B", NodeParameterValue.Float)
        self._addOutput("Mul Output", "Value", NodeParameterValue.Float)
