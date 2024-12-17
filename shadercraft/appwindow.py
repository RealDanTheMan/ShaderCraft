import sys
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QMainWindow
from PySide6.QtCore import Qt
from .windowbase import Ui_MainWindow
from .node import Node
from .stdnodes import FloatNode, MulNode


class AppWindow(QMainWindow):
    def __init__(self) -> None:
        super(AppWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.NodeGraphView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.NodeGraphView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.NodeGraphView.setDragMode(QGraphicsView.NoDrag)

        self.__nodes: list[Node] = []
        self.__scene = QGraphicsScene()
        self.ui.NodeGraphView.setScene(self.__scene)
        self.__addTestNodes()

    def addNode(self, node: Node) -> None:
        """Adds given node to this app scene view"""
        assert (node is not None)
        self.__nodes.append(node)
        node.initWidget()
        if node.getWidget():
            self.__scene.addItem(node.getWidget())

    def __addTestNodes(self) -> None:
        """Create number of nodes useful for testing the application"""
        node0 = MulNode()
        node1 = FloatNode()
        node2 = FloatNode()

        self.addNode(node0)
        self.addNode(node1)
        self.addNode(node2)

        node0.setPosition(-200, 200)
        node1.setPosition(300, -100)
        node2.setPosition(0, 0)
