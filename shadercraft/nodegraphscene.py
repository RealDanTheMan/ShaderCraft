from __future__ import annotations
from typing import Optional
from uuid import UUID, uuid1

import PySide6
from .node import Node, NodeConnection, NodeIO
from .node_widget import NodeWidget, NodePin
from .shadernodes import FloatShaderNode, MulShaderNode
from .asserts import assertRef, assertFalse, assertTrue
from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import Signal, Slot


class NodeGraphScene(QGraphicsScene):
    """
    Class that represents node graph scene.
    All the nodes and their connections are stored in the scene
    """
    def __init__(self):
        """Default constructor"""
        super().__init__()
        self.__nodes: list[Node] = []
        self.__names: list[str] = []
        self.__names_lookup: dict[str, int] = {}
        self.__drag_pin: Optional[NodePin] = None
        self.__drop_pin: Optional[NodePin] = None
        self.__addTestNodes()

    def addNode(self, node: Node) -> None:
        """
        Add node to this node graph.
        Added node will be renamed if needed to ensure name uniquness.
        """
        assertRef(node)
        assertFalse(node in self.__nodes, "Node already present in the scene")

        self.assignNodeName(node)
        self.__nodes.append(node)
        node.connectionAdded.connect(self.onNodeConnectionAdded)
        node.connectionRemoved.connect(self.onNodeConnectionRemoved)
        if node.getWidget() is None:
            node.initWidget()
        self.addItem(node.getWidget())
        print(f"NodeGraphScene: Adding new node -> {node.uuid}")

    def __addTestNodes(self) -> None:
        """Create and add set of node to the scene, usefull for testing"""
        node0 = MulShaderNode()
        node1 = FloatShaderNode()
        node2 = FloatShaderNode()

        self.addNode(node0)
        self.addNode(node1)
        self.addNode(node2)

        node0.setPosition(-200, 200)
        node1.setPosition(300, -100)
        node2.setPosition(0, 0)

    def getAllNodes(self) -> list[Node]:
        """Get list of all nodes present in the graph"""
        return list(self.__nodes)

    def getNodeFromWidget(self, widget: NodeWidget) -> Optional[Node]:
        """Get handle to the node linked to given node widget"""

        assertRef(widget)
        match = [node for node in self.__nodes if node.getWidget() is widget]
        if match:
            return match[0]
        return None

    def getNodeFromWidgetUUID(self, uuid: UUID) -> Optional[Node]:
        """Get node linked to widget that matches given widget UUID"""

        assertRef(uuid)
        widget = self.getWidgetFromUUID(uuid)
        if widget:
            return self.getNodeFromWidget(widget)
        return None

    def getWidgetFromUUID(self, uuid: UUID) -> Optional[NodeWidget]:
        """Get node widget matching given UUID"""

        assertRef(uuid)
        match = [node.getWidget() for node in self.__nodes if node.getWidget() and node.getWidget().uuid is uuid]
        assertTrue(len(match) <= 1)
        if match:
            return match[0]
        return None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Event handler invoked when mouse button press happens inside the graph"""
        item = self.itemAt(event.scenePos(), self.views()[0].transform())
        if item and isinstance(item, NodePin):
            self.beginPinDragDrop(item)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Event handler invoked when the mouse button release happens inside the graph"""
        item = self.itemAt(event.scenePos(), self.views()[0].transform())
        if item and isinstance(item, NodePin):
            self.endPinDragDrop(item)
        else:
            super().mouseReleaseEvent(event)

    def beginPinDragDrop(self, pin: NodePin) -> None:
        """Start of node pin drag & drop event flow"""
        assertRef(pin)
        print(f"Node pin drag registered [pin:{pin.uuid}]")
        self.__drag_pin = pin
        self.__drop_pin = None

    def endPinDragDrop(self, pin: NodePin) -> None:
        """End of node pin drag & drop event flow"""
        assertRef(pin)
        print(f"Node pin drop registered [pin:{pin.uuid}]")
        self.__drop_pin = pin
        self.finalisePinDragDrop()

    def resetPinDragDrop(self) -> None:
        """Resets node pin drag & drop event flow"""
        self.__drag_pin = None
        self.__drop_pin = None

    def finalisePinDragDrop(self) -> None:
        """Finalise node pin drag & drop event and create connection if valid"""
        a = self.__drag_pin
        b = self.__drop_pin
        if a is None or b is None:
            print("Aborting pin drag & drop: one or more pins are invalid")
            self.resetPinDragDrop()
            return

        if a.role is not NodePin.Role.OUTPUT:
            print("Aborting pin drag & drop: source pin is not of output type")
            return

        if b.role is not NodePin.Role.INPUT:
            print("Aborting pin drag & drop: target pin is not of input type")
            return

        if a.node_uuid is b.node_uuid:
            print("Aborting pin drag & drop: pins share parents")
            self.resetPinDragDrop()
            return

        if a.uuid is b.uuid:
            print("Aborting pin drag & drop: pins are the same")
            self.resetPinDragDrop()
            return

        self.attemptNodeConnection(a, b)
        self.resetPinDragDrop()

    def attemptNodeConnection(self, pinout: NodePin, pinin: NodePin) -> bool:
        """Attempts to connect two node via input/output pins"""
        assertRef(pinout)
        assertRef(pinin)
        print(f"Attempting node connection: {pinout.uuid} -> {pinin.uuid}")

        inode: Optional[Node] = self.getNodeFromWidgetUUID(pinin.node_uuid)
        onode: Optional[Node] = self.getNodeFromWidgetUUID(pinout.node_uuid)
        if inode is None or onode is None:
            print("Connection cancelled, could not resolve node from pins")
            return False

        node_in: Optional[NodeIO] = inode.getNodeInput(pinin.uuid)
        node_out: Optional[NodeIO] = onode.getNodeOutput(pinout.uuid)
        if node_in is None or node_out is None:
            print("Connection cancelled, failed to resolve node inputs/outputs")
            return False

        inode.addConnection(node_in.uuid, onode, node_out.uuid)
        return True

    def onNodeConnectionAdded(self, connection: NodeConnection) -> None:
        """Event handler invoked when new connection between two nodes happens in the graph"""
        assertRef(connection)
        assertRef(connection.getWidget)
        self.addItem(connection.getWidget())

    def onNodeConnectionRemoved(self, connection: NodeConnection) -> None:
        """Event handler invoked when existing connection between nodes is severed"""
        assertRef(connection)
        assertRef(connection.getWidget())
        self.removeItem(connection.getWidget())

    def assignNodeName(self, node: Node) -> str:
        """Generates unqiue node name"""
        if node.name not in self.__names:
            self.__names_lookup[node.name] = 0
            self.__names.append(node.name)
            return node.name
        else:
            self.__names_lookup[node.name] += 1
            name = f"{node.name}_{self.__names_lookup[node.name]}"
            self.__names.append(name)
            node.name = name
            return name
