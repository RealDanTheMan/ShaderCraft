from __future__ import annotations
from typing import Optional, Type
from dataclasses import dataclass
from collections import OrderedDict
from uuid import UUID, uuid1
from enum import Enum
import logging as Log
from PySide6.QtCore import QObject, QPointF, Slot, Signal

from .connection_widget import ConnectionWidget
from .node_widget import NodeProxyWidget, NodePropetyInfo
from .asserts import assertRef, assertTrue, assertType


@dataclass
class NodeValue:
    """
    Class that encapsulates values passed between nodes.
    Values can be passed between node inputs/outputs via connections.
    """
    __no_value: NodeValue

    def __init__(self, value_type, value) -> None:
        self.value_type = value_type
        self.value = value

    @classmethod
    def noValue(cls) -> NodeValue:
        """Get static value object representing no value"""
        if cls.__no_value is None:
            cls.__no_value = NodeValue(None, None)
        return cls.__no_value


@dataclass
class NodeIO:
    """
    Class representing node inputs or outputs.
    Inputs and outputs is how we can connection nodes and build logic.
    """

    def __init__(self):
        self.uuid: UUID = uuid1()
        self.name: str = None
        self.label: str = None

    def getInfo(self) -> NodePropetyInfo:
        """Get minimal information representing this connection"""
        return NodePropetyInfo(self.uuid, self.label)

    @staticmethod
    def create(name: str, label: str) -> NodeIO:
        """Shorthand function for creating node input/outputs"""
        inout = NodeIO()
        inout.uuid = uuid1()
        inout.name = name
        inout.label = label
        return inout


class NodeConnection():
    """Class representing singular connection between owner node and nother"""

    def __init__(self, src: Node, src_uuid: UUID, target: Node, target_uuid: UUID):
        assertRef(src)
        assertRef(src_uuid)
        assertRef(target)
        assertRef(target_uuid)

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
        assertRef(self.source.getWidget())
        assertRef(self.target.getWidget())

        start: QPointF = self.source.getWidget().getPinScenePos(self.source_uuid)
        end: QPointF = self.target.getWidget().getPinScenePos(self.target_uuid)
        assertRef(start)
        assertRef(end)

        widget = ConnectionWidget(self.uuid, start, end)
        return widget

    def getWidget(self) -> ConnectionWidget:
        """Get reference to widget linked to this node connection"""
        return self._widget

    def getSourceValue(self) -> Optional[NodeValue]:
        """Get node value from source end of this connection"""
        assertRef(self.source)
        assertRef(self.source.uuid)

        value = self.source.getNodeOutputValue(self.source_uuid)
        assertRef(value)
        return value

    @Slot(QPointF)
    def onConnectedNodePositionChanged(self, value: QPointF) -> None:
        """Event handler invoked when either source or target node changes position"""
        assertRef(self.getWidget())
        assertRef(value)
        assertRef(self.source.getWidget())
        assertRef(self.target.getWidget())

        start: QPointF = self.source.getWidget().getPinScenePos(self.source_uuid)
        end: QPointF = self.target.getWidget().getPinScenePos(self.target_uuid)
        assertRef(start)
        assertRef(end)

        self.getWidget().updateConnectionPoints(start, end)


class Node(QObject):
    """
    Class that encapsulates base node implementation.
    Nodes can be added to the node graph scene and connected via their input/output to
    produce logic.
    """
    label: str = "Node Label"
    connectionAdded = Signal(NodeConnection)
    connectionRemoved = Signal(NodeConnection)
    selectionChanged = Signal(QObject, bool)
    positionChanged = Signal(QPointF)

    def __init__(self) -> None:
        QObject.__init__(self, None)

        self.name: str = "Node_Name"
        self.uuid: UUID = uuid1()
        self.widget: NodeProxyWidget = None
        self.posx: float = 0.0
        self.posy: float = 0.0

        self.__outputs: dict[UUID, NodeIO] = {}
        self.__inputs: dict[UUID, NodeIO] = {}
        self.__connections: list[NodeConnection] = []
        self.__selected: bool = False

    def _registerInput(self, node_input: NodeIO) -> NodeIO:
        assertRef(node_input)
        assertRef(node_input.uuid)
        if node_input.uuid in self.__inputs:
            raise ValueError("Node input with matching UUID already exists!")

        self.__inputs[node_input.uuid] = node_input
        return self.__inputs[node_input.uuid]

    def _registerOutput(self, node_output: NodeIO) -> NodeIO:
        assertRef(node_output)
        assertRef(node_output.uuid)
        if node_output.uuid in self.__outputs:
            raise ValueError("Node output with matching UUID already exists!")

        self.__outputs[node_output.uuid] = node_output
        return self.__outputs[node_output.uuid]

    def getNodeInput(self, uuid: UUID) -> Optional[NodeIO]:
        """Get node input which matches given UUID"""
        assertRef(uuid)
        if uuid not in self.__inputs:
            return None
        return self.__inputs[uuid]

    def getNodeInputs(self) -> list[NodeIO]:
        """Get list of all node inputs"""
        return list(self.__inputs.values())

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
            return self._generateInputValue(node_in)
        return None

    def _generateInputValue(self, node_input: NodeIO) -> NodeValue:
        """Generate default input value for given input property of the node"""
        assertRef(node_input)
        return NodeValue.noValue()

    def getNodeOutput(self, uuid: UUID) -> Optional[NodeIO]:
        """Get node output which matches given UUID"""
        assertRef(uuid)
        if uuid not in self.__outputs:
            return None
        return self.__outputs[uuid]

    def getNodeOutputs(self) -> list[NodeIO]:
        """Get list of all node outputs"""
        return list(self.__outputs.values())

    def getNodeOutputValue(self, uuid: UUID) -> Optional[NodeValue]:
        """Get value for node output matching given UUID"""
        output = self.getNodeOutput(uuid)
        if output is not None:
            return self._generateOutput(output)
        return None

    def _generateOutput(self, node_output: NodeIO) -> NodeValue:
        """
        Generates output value for given node output.

        Derived class should implement this for all node outputs.
        """
        assertRef(node_output)
        return NodeValue.noValue()

    def addConnection(self, uuid: UUID, src: Node, src_uuid: UUID) -> bool:
        """Add new connection between this node intput and another node output."""
        assertRef(uuid)
        assertRef(src)
        assertRef(src_uuid)

        if self.getConnection(uuid):
            Log.debug("Connection rejected, connection already exists for this input")
            return False
        con = NodeConnection(src, src_uuid, self, uuid)
        self.__connections.append(con)
        self.connectionAdded.emit(con)

        return True

    def removeConnection(self, uuid: UUID) -> None:
        """Remove node connection matching given UUID"""
        assertRef(uuid)
        con: NodeConnection = self.getConnection(uuid)
        if con is not None:
            Log.debug(f"Removing node connection: {uuid}")
            self.__connections.remove(con)
            self.connectionRemoved.emit(con)

    def getConnection(self, uuid: UUID) -> Optional[NodeConnection]:
        """Get connection on this node that matches given UUID"""
        for con in self.__connections:
            if con.uuid == uuid:
                return con
        return None

    def getConnectionFromInput(self, node_in: NodeIO) -> Optional[NodeConnection]:
        """Get connection on this node given input on this node forms traget of the connection"""
        for con in self.__connections:
            if con.target_uuid == node_in.uuid:
                return con
        return None

    def getAllConnections(self) -> list[NodeConnection]:
        """Get all input connection from this node"""
        return list(self.__connections)

    def initWidget(self) -> None:
        """Create widget object representing this node"""
        input_infos: list[NodePropetyInfo] = [i.getInfo() for i in self.__inputs.values()]
        output_infos: list[NodePropetyInfo] = [i.getInfo() for i in self.__outputs.values()]

        self.widget = NodeProxyWidget(self.uuid, input_infos, output_infos)
        self.widget.getWidget().setLabelText(self.label)
        self.widget.getWidget().setNameText(self.name)
        self.widget.positionChanged.connect(self.onWidgetPositionChanged)
        self.widget.selectionChanged.connect(self.onWidgetSelectionChanged)

    def getWidget(self) -> NodeProxyWidget:
        """Get handle to the widget representing this node"""
        return self.widget

    @Slot(QPointF)
    def onWidgetPositionChanged(self, value: QPointF) -> None:
        """Event handler invoked when bound widget changes position"""
        assertRef(value)
        assertType(value, QPointF)

        self.posx = value.x()
        self.posy = value.y()
        self.positionChanged.emit(QPointF(self.posx, self.posy))

    @Slot(bool)
    def onWidgetSelectionChanged(self, value: bool) -> None:
        """Event handler invoked when the widget bound to this node changes its selection state"""
        self.__selected = value
        self.selectionChanged.emit(self, value)

    def setPosition(self, x: float, y: float) -> None:
        """Upadate position of this node, will also update widget position"""
        assertType(x, float)
        assertType(y, float)

        self.posx = x
        self.posy = y
        if self.widget:
            self.widget.setPos(QPointF(x, y))
        self.positionChanged.emit(QPointF(x, y))

    def getDownstreamNodes(self) -> list[Node]:
        """Recursively gets list of this node down stream descendants"""
        nodes: list[Node] = []
        for node_in in self.getNodeInputs():
            con: Optional[NodeConnection] = self.getConnectionFromInput(node_in)
            if con:
                child_nodes: list[Node] = con.source.getDownstreamNodes()
                nodes.extend(child_nodes)
        nodes.append(self)
        nodes = list(OrderedDict.fromkeys(nodes))
        return nodes

    def getSelectedStatate(self) -> bool:
        """Get value indicating if this node is currently selected or not"""
        return self.__selected


@dataclass
class NodeClassDesc:
    """
    Utility class for handling and passing around node class values.
    """
    label:str = None
    node_type: Type[Node] = None

    @staticmethod
    def fromNodeClass(node_cls: Type[Node]) -> NodeClassDesc:
        """Create node class desctiption based on given node type"""
        assertRef(node_cls)
        desc: NodeClassDesc = NodeClassDesc()
        desc.label = node_cls.label
        desc.node_type = node_cls
        return desc

    @staticmethod
    def fromNode(node: Node) -> NodeClassDesc:
        """Create node class description based on given node instance"""
        assertRef(node)
        assertTrue(isinstance(node, Node))
        desc: NodeClassDesc = NodeClassDesc()
        desc.label = node.label
        desc.node_type = type(node)
