import sys
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QMainWindow
from PySide6.QtCore import Qt
from .windowbase import Ui_MainWindow
from .nodegraphscene import NodeGraphScene
from .node import Node
from .stdnodes import FloatNode, MulNode
from .nodegraphview import NodeGraphView

class AppWindow(QMainWindow):
    def __init__(self) -> None:
        super(AppWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Create and setup node graph viewport
        self.NodeGraphView: NodeGraphView = NodeGraphView()
        self.NodeGraphView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.NodeGraphView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.NodeGraphView.setDragMode(QGraphicsView.NoDrag)
        self.ui.NodeGraphFrame.layout().addWidget(self.NodeGraphView)

        self.NodeGraph: NodeGraphScene = NodeGraphScene()
        self.NodeGraphView.setScene(self.NodeGraph)
