import sys
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView

from .node_widget import NodeWidget

class AppWindow(object):
    def __init__(self) -> None:
        self.__app = QApplication(sys.argv)
        self.__test_node = NodeWidget()
        self.__scene = QGraphicsScene()
        self.__scene.addItem(self.__test_node)
        self.__view = QGraphicsView(self.__scene)
        self.__view.setWindowTitle("Shader Craft")
        self.__view.resize(800, 600)
        self.__view.show()

    def run(self) -> None:
        err_code = self.__app.exec()
        sys.exit(err_code)