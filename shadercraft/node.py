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


class NodeValue(object):
    __noValue: NodeValue
    def __init__(self, value_type, value) -> None:
        self.value_type = value_type
        self.value = value

    @classmethod
    def NoValue(cls) -> NodeValue:
        if cls.__noValue is None:
            cls.__noValue = NodeValue(None, None)
        return cls.__noValue



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

        self.source.positionChanged.connect(self.onConnectedNodePositionChanged)
        self.target.positionChanged.connect(self.onConnectedNodePositionChanged)

    def _createWidget(self) -> ConnectionWidget:
        """Create a widget representing this connection line on the graph"""
        startpin = self.source.getWidget().getOutputPin(self.source_uuid)
        endpin = self.target.getWidget().getInputPin(self.target_uuid)
        widget = ConnectionWidget(startpin, endpin, self.uuid)
        return widget

    def getWidget(self) -> ConnectionWidget:
        """Get reference to widget linked to this node connection"""
        return self._widget

    def getSourceValue(self) -> Optional[NodeValue]:
        """Get node value from source end of this connection"""
        assert (self.source is not None)
        assert (self.source_uuid is not None)

        value = self.source.getNodeOutputValue(self.source_uuid)
        assert (value is not None)
        return value

    @Slot(QPointF)
    def onConnectedNodePositionChanged(self, value: QPointF) -> None:
        """Event handler invoked when either source or target node changes position"""
        assert (self.getWidget() is not None)
        # Trigger widget re-draw
        self.getWidget().prepareGeometryChange()
        self.getWidget().update()


class Node(QObject):
    connectionAdded = Signal(NodeConnection)
    connectionRemoved = Signal(NodeConnection)
    positionChanged = Signal(QPointF)

    def __init__(self) -> None:
        QObject.__init__(self, None)

        self.label: str = "Node Label"
        self.name: str = "Node_Name"
        self.uuid: UUID = uuid1()
        self.widget: NodeWidget = None
        self.posx: float = 0.0
        self.posy: float = 0.0

        self.__outputs: list[NodeInputOutput] = []
        self.__inputs: list[NodeInputOutput] = []
        self.__connections: list[NodeConnection] = []

    def _addOutput(self, name: str, label: str, type: NodeParameterValue) -> NodeInputOutput:
        """Add new value output for this node"""
        assert (name is not None)
        assert (label is not None)
        assert (type is not NodeParameterValue.NoValue)

        node_out = NodeInputOutput.create(name, label, type)
        self.__outputs.append(node_out)
        return node_out

    def _addInput(self, name: str, label: str, type: NodeParameterValue) -> NodeInputOutput:
        """Add new value input for this node"""
        assert (name is not None)
        assert (label is not None)
        assert (type is not NodeParameterValue.NoValue)

        node_in = NodeInputOutput.create(name, label, type)
        self.__inputs.append(node_in)
        return node_in

    def getNodeInput(self, uuid: UUID) -> Optional[NodeInputOutput]:
        """Get node input which matches given UUID"""
        assert (uuid is not None)
        for input in self.__inputs:
            if input.uuid == uuid:
                return input
        return None

    def getNodeInputs(self) -> list[NodeInputOutput]:
        """Get list of all node inputs"""
        return list(self.__inputs)

    def getNodeInputValue(self, uuid: UUID) -> Optional[NodeValue]:
        """
        Get value stored in this node input of matching UUID

        If the input matching given UUID has connection the value will be 
        resolved from the source end of the connection.

        None return value indicates there is no input on this node matching given UUID.
        """
        node_in = self.getNodeInput(uuid)
        if node_in is not None:
            con = self.getConnectionFromInput(node_in)
            if con:
                return con.getSourceValue()
            else:
                return self._generateInputValue(node_in)
        else:
            return None

    def _generateInputValue(self, node_input: NodeInputOutput) -> NodeValue:
        """Generate default input value for given input property of the node"""
        return NodeValue.NoValue()

    def getNodeOutput(self, uuid: UUID) -> Optional[NodeInputOutput]:
        """Get node output which matches given UUID"""
        for output in self.__outputs:
            if output.uuid == uuid:
                return output
        return None

    def getNodeOutputs(self) -> list[NodeInputOutput]:
        """Get list of all node outputs"""
        return list(self.__outputs)

    def getNodeOutputValue(self, uuid: UUID) -> Optional[NodeValue]:
        """Get value for node output matching given UUID"""
        output = self.getNodeOutput(uuid)
        if output is not None:
            return self._generateOutput(output)
        else:
            return None

    def _generateOutput(self, node_output: NodeInputOutput) -> NodeValue:
        """
        Generates output value for given node output.

        Derived class should implement this for all node outputs.
        """
        return NodeValue.NoValue()

    def addConnection(self, uuid: UUID, src: Node, src_uuid: UUID) -> bool:
        """Add new connection between this node intput and another node output."""
        assert (uuid)
        assert (src)
        assert (src_uuid)

        if self.getConnection(uuid):
            print("Connection rejected, connection already exists for this input")
            return False
        
        con = NodeConnection(src, src_uuid, self, uuid)
        self.__connections.append(con)
        self.connectionAdded.emit(con)

        return True

    def getConnection(self, uuid: UUID) -> Optional[NodeConnection]:
        """Get connection on this node that matches given UUID"""
        for con in self.__connections:
            if con.uuid == uuid:
                return con
        return None

    def getConnectionFromInput(self, node_in: NodeInputOutput) -> Optional[NodeConnection]:
        """Get connection on this node given input on this node forms traget of the connection"""
        for con in self.__connections:
            if con.target_uuid == node_in.uuid:
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
        self.positionChanged.emit(QPointF(self.posx, self.posy))

    def setPosition(self, x: float, y: float) -> None:
        """Upadate position of this node, will also update widget position"""
        self.posx = x
        self.posy = y
        if self.widget:
            self.widget.setPos(QPointF(x, y))
        self.positionChanged.emit(QPointF(x, y))
