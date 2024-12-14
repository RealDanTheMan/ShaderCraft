from enum import Enum
from PySide6.QtCore import QPointF, Slot
from .node_widget import NodeWidget


class NodeParameterValue(Enum):
    NoValue = 0
    Float = 1
    Float2 = 2
    Float3 = 3
    Float4 = 4


class NodeInputOutput(object):
    def __init__(self):
        self.name: str = None
        self.label: str = None
        self.valueType: NodeParameterValue = NodeParameterValue.NoValue


class Node(object):
    def __init__(self) -> None:
        self.label: str = "Node Label"
        self.name: str = "Node Name"
        self.guid: int = 0
        self.widget: NodeWidget = None
        self.posx: float = 0.0
        self.posy: float = 0.0

        self.__outputs: list[NodeInputOutput] = []
        self.__inputs: list[NodeInputOutput] = []

    def addOutput(self, name: str, label: str, type: NodeParameterValue):
        assert (name is not None)
        assert (label is not None)
        assert (type is not NodeParameterValue.NoValue)

        output = NodeInputOutput()
        output.name = name
        output.label = label
        output.valueType = type
        self.__outputs.append(output)

    def addInput(self, name: str, label: str, type: NodeParameterValue):
        assert (name is not None)
        assert (label is not None)
        assert (type is not NodeParameterValue.NoValue)

        input = NodeInputOutput()
        input.name = name
        input.label = label
        input.valueType = type
        self.__inputs.append(input)

    def initWidget(self) -> None:
        """Create widget object representing this node"""
        self.widget = NodeWidget()
        self.widget.setLabelText(self.label)
        self.widget.positionChanged.connect(self.onWidgetPositionChanged)

    def getWidget(self) -> NodeWidget:
        """Get handle to the widget representing this node"""
        return self.widget

    @Slot(QPointF)
    def onWidgetPositionChanged(self, value: QPointF) -> None:
        """Event handler invoked when bound widget changes position"""
        self.posx = value.x()
        self.posy = value.y()

    def setPosition(self, x: float, y: float) -> None:
        """Upadate position of this node, will also update widget position"""
        self.posx = x
        self.posy = y
        if self.widget:
            self.widget.setPos(QPointF(x, y))
