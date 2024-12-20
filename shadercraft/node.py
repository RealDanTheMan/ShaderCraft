from __future__ import annotations
from typing import Optional
from uuid import UUID, uuid1
from enum import Enum
from PySide6.QtCore import QObject, QPointF, Slot, Signal

from shadercraft.connection_widget import ConnectionWidget
from .node_widget import NodeWidget, NodePin

class NodeParameterValue(Enum):
    NoValue = 0
    Float = 1
    Float2 = 2
    Float3 = 3
    Float4 = 4


class NodeInputOutput(object):
    """
    Class representing node inputs or outputs.
    Inputs and outputs is how we can connection nodes and build logic.
    """
    def __init__(self):
        self.uuid: UUID = uuid1()
        self.name: str = None
        self.label: str = None
        self.valueType: NodeParameterValue = NodeParameterValue.NoValue

    @staticmethod
    def create(name: str, label: str, value: NodeParameterValue) -> NodeInputOutput:
        """Shorthand function for creating node input/outputs"""
        inout = NodeInputOutput()
        inout.uuid = uuid1()
        inout.name = name
        inout.label = label
        inout.valueType = value
        return inout

class NodeConnection(object):
    """Class representing singular connection between owner node and nother"""
    def __init__(self, src: Node, src_uuid: UUID, target: Node, target_uuid: UUID):
        self.uuid = uuid1()
        self.source: Node = src
        self.source_uuid: UUID = src_uuid
        self.target: Node = target
        self.target_uuid = target_uuid
        self._widget: ConnectionWidget = self._createWidget()

    def _createWidget(self) -> ConnectionWidget:
        startpin = self.source.getWidget().getOutputPin(self.source_uuid)
        endpin = self.target.getWidget().getInputPin(self.target_uuid)
        widget = ConnectionWidget(startpin, endpin, self.uuid)
        return widget

    def getWidget(self) -> ConnectionWidget:
        return self._widget


class Node(QObject):
    connectionAdded = Signal(NodeConnection)
    connectionRemoved = Signal(NodeConnection)

    def __init__(self) -> None:
        QObject.__init__(self, None)

        self.label: str = "Node Label"
        self.name: str = "Node Name"
        self.uuid: UUID = uuid1()
        self.widget: NodeWidget = None
        self.posx: float = 0.0
        self.posy: float = 0.0

        self.__outputs: list[NodeInputOutput] = []
        self.__inputs: list[NodeInputOutput] = []
        self.__connection: list[NodeConnection] = []

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

    def getNodeInput(self, uuid: UUID) -> Optional[NodeInputOutput]:
        """Get node input which matches given UUID"""
        assert (uuid is not None)
        for input in self.__inputs:
            if input.uuid == uuid:
                return input
        return None

    def getNodeOutput(self, uuid: UUID) -> Optional[NodeInputOutput]:
        """Get node output which matches given UUID"""
        for output in self.__outputs:
            if output.uuid == uuid:
                return output
        return None

    def addConnection(self, uuid: UUID, src: Node, src_uuid: UUID) -> bool:
        assert (uuid)
        assert (src)
        assert (src_uuid)

        if self.getConnection(uuid):
            print("Connection rejected, connection already exists for this input")
            return False
        
        con = NodeConnection(src, src_uuid, self, uuid)
        self.__connection.append(con)
        self.connectionAdded.emit(con)

        return True

    def getConnection(self, uuid: UUID) -> Optional[NodeConnection]:
        for con in self.__connection:
            if con.uuid == uuid:
                return con
        return None

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
