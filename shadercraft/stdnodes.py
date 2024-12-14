from .node import Node, NodeParameterValue


class FloatNode(Node):
    def __init__(self):
        super().__init__()

        self.name = "Float Node"
        self.label = "Float"
        self.addOutput("Float Output", "Float", NodeParameterValue.Float)
