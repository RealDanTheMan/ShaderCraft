import sys
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView
from .node import Node


class AppWindow(object):
    def __init__(self) -> None:
        self.__app = QApplication(sys.argv)
        self.__nodes: list[Node] = []
        self.__scene = QGraphicsScene()
        self.__view = QGraphicsView(self.__scene)
        self.__view.setWindowTitle("Shader Craft")
        self.__view.resize(800, 600)
        self.__view.show()
        self.__addTestNodes()

    def run(self) -> None:
        """Main loop method for this application window, not blocking"""
        err_code = self.__app.exec()
        sys.exit(err_code)

    def addNode(self, node: Node) -> None:
        """Adds given node to this app scene view"""
        assert (node is not None)
        self.__nodes.append(node)
        node.initWidget()
        if node.getWidget():
            self.__scene.addItem(node.getWidget())

    def __addTestNodes(self) -> None:
        """Create number of nodes useful for testing the application"""
        node0 = Node()
        node1 = Node()
        node2 = Node()

        self.addNode(node0)
        self.addNode(node1)
        self.addNode(node2)

        node0.setPosition(-200, 200)
        node1.setPosition(300, -100)
        node2.setPosition(0, 0)
