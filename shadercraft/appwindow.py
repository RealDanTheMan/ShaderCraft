import sys
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView

from .node import Node

class AppWindow(object):
    def __init__(self) -> None:
        self.__app = QApplication(sys.argv)
        self.__test_node = Node()
        self.__test_node.initWidget()
        self.__scene = QGraphicsScene()
        self.__scene.addItem(self.__test_node.getWidget())
        self.__view = QGraphicsView(self.__scene)
        self.__view.setWindowTitle("Shader Craft")
        self.__view.resize(800, 600)
        self.__view.show()

    def run(self) -> None:
        err_code = self.__app.exec()
        sys.exit(err_code)
