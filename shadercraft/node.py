from __future__ import annotations
import uuid
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
        self.uuid: uuid.UUID = uuid.uuid1()
        self.name: str = None
        self.label: str = None
        self.valueType: NodeParameterValue = NodeParameterValue.NoValue

    @staticmethod
    def create(name: str, label: str, value: NodeParameterValue) -> NodeInputOutput:
        """Shorthand function for creating node input/outputs"""
        inout = NodeInputOutput()
        inout.uuid = uuid.uuid1()
        inout.name = name
        inout.label = label
        inout.valueType = value
        return inout


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

    def _addOutput(self, name: str, label: str, type: NodeParameterValue):
        """Add new value output for this node"""
        assert (name is not None)
        assert (label is not None)
        assert (type is not NodeParameterValue.NoValue)

        output = NodeInputOutput.create(name, label, type)
        self.__outputs.append(output)

    def _addInput(self, name: str, label: str, type: NodeParameterValue):
        """Add new value input for this node"""
        assert (name is not None)
        assert (label is not None)
        assert (type is not NodeParameterValue.NoValue)

        input = NodeInputOutput.create(name, label, type)
        self.__inputs.append(input)

    def initWidget(self) -> None:
        """Create widget object representing this node"""
        self.widget = NodeWidget()
        self.widget.setLabelText(self.label)
        self.widget.addInputs([i.uuid for i in self.__inputs])
        self.widget.addOutputs([i.uuid for i in self.__outputs])
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
