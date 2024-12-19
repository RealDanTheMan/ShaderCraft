import sys
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QMainWindow
from PySide6.QtCore import Qt
from .windowbase import Ui_MainWindow
from .nodegraphscene import NodeGraphScene
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

        self.NodeGraph: NodeGraphScene = NodeGraphScene()
        self.ui.NodeGraphView.setScene(self.NodeGraph)
