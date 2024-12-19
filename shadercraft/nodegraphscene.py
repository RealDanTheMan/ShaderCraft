from .node import Node
from .stdnodes import FloatNode, MulNode
from PySide6.QtWidgets import QGraphicsScene


class NodeGraphScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.__nodes: [Node] = []
        self.__addTestNodes()

    def addNode(self, node: Node) -> None:
        """Add node to this node graph"""
        assert (node is not None)
        assert (node not in self.__nodes)

        self.__nodes.append(node)
        if node.getWidget() is None:
            node.initWidget()
        self.addItem(node.getWidget())
        print(f"NodeGraphScene: Adding new node -> {node.uuid}")

    def __addTestNodes(self) -> None:
        node0 = MulNode()
        node1 = FloatNode()
        node2 = FloatNode()

        self.addNode(node0)
        self.addNode(node1)
        self.addNode(node2)

        node0.setPosition(-200, 200)
        node1.setPosition(300, -100)
        node2.setPosition(0, 0)
