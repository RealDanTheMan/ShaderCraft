from __future__ import annotations
from typing import Optional
from uuid import UUID, uuid1

import PySide6
from .node import Node, NodeConnection, NodeInputOutput
from .node_widget import NodeWidget, NodePin
from .shadernodes import FloatShaderNode, MulShaderNode
from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import Signal, Slot


class NodeGraphScene(QGraphicsScene):
    def __init__(self):
        """Default constructor"""
        super().__init__()
        self.__nodes: list[Node] = []
        self.__addTestNodes()
        self.__pinDragDropSource: Optional[NodePin] = None
        self.__pinDragDropTarget: Optional[NodePin] = None

    def addNode(self, node: Node) -> None:
        """Add node to this node graph"""
        assert (node is not None)
        assert (node not in self.__nodes)

        self.__nodes.append(node)
        node.connectionAdded.connect(self.onNodeConnectionAdded)
        node.connectionRemoved.connect(self.OnNodeConnectionRemoved)
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
        return list(self.__nodes)

    def getNodeFromWidget(self, widget: NodeWidget) -> Optional[Node]:
        """Get handle to the node linked to given node widget"""
        match = [node for node in self.__nodes if node.getWidget() is widget]
        if match:
            return match[0]
        else:
            return None

    def getNodeFromWidgetUUID(self, uuid: UUID) -> Optional[Node]:
        """Get node linked to widget that matches given widget UUID"""
        widget = self.getWidgetFromUUID(uuid)
        if widget:
            return self.getNodeFromWidget(widget)
        else:
            return None

    def getWidgetFromUUID(self, uuid: UUID) -> Optional[NodeWidget]:
        """Get node widget matching given UUID"""
        match = [node.getWidget() for node in self.__nodes if node.getWidget() and node.getWidget().uuid is uuid]
        assert (len(match) <= 1)
        if match:
            return match[0]
        else:
            return None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        item = self.itemAt(event.scenePos(), self.views()[0].transform()) 
        if item and isinstance(item, NodePin):
            self.beginPinDragDrop(item)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        item = self.itemAt(event.scenePos(), self.views()[0].transform())
        if item and isinstance(item, NodePin):
            self.endPinDragDrop(item)
        else:
            super().mouseReleaseEvent(event)

    def beginPinDragDrop(self, pin: NodePin) -> None:
        """Start of node pin drag & drop event flow"""
        assert (pin is not None)
        print(f"Node pin drag registered [pin:{pin.uuid}]")
        self.__pinDragDropSource = pin
        self.__pinDragDropTarget = None

    def endPinDragDrop(self, pin: NodePin) -> None:
        """End of node pin drag & drop event flow"""
        assert (pin is not None)
        print(f"Node pin drop registered [pin:{pin.uuid}]")
        self.__pinDragDropTarget = pin
        self.finalisePinDragDrop()

    def resetPinDragDrop(self) -> None:
        """Resets node pin drag & drop event flow"""
        self.__pinDragDropSource = None
        self.__pinDragDropTarget = None

    def finalisePinDragDrop(self) -> None:
        """Finalise node pin drag & drop event and create connection if valid"""
        a = self.__pinDragDropSource
        b = self.__pinDragDropTarget
        if a is None or b is None:
            print("Aborting pin drag & drop: one or more pins are invalid")
            self.resetPinDragDrop()
            return

        if not a.role is NodePin.Role.EOutput:
            print("Aborting pin drag & drop: source pin is not of output type")
            return None

        if not b.role is NodePin.Role.EInput:
            print("Aborting pin drag & drop: target pin is not of input type")
            return None

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
        assert (pinout is not None)
        assert (pinin is not None)
        print(f"Attempting node connection: {pinout.uuid} -> {pinin.uuid}")

        inode: Optional[Node] = self.getNodeFromWidgetUUID(pinin.node_uuid)
        onode: Optional[Node] = self.getNodeFromWidgetUUID(pinout.node_uuid)
        if inode is None or onode is None:
            print("Connection cancelled, could not resolve node from pins")
            return False

        input: Optional[NodeInputOutput] = inode.getNodeInput(pinin.uuid)
        output: Optional[NodeInputOutput] = onode.getNodeOutput(pinout.uuid)
        if input is None or output is None:
            print("Connection cancelled, failed to resolve node inputs/outputs")
            return False
        if input.valueType is not output.valueType:
            print("Connection cancelled, input/output does not have common value type")
            return False
       
        inode.addConnection(input.uuid, onode, output.uuid)
        return True

    def onNodeConnectionAdded(self, connection: NodeConnection)  -> None:
        assert (connection)
        assert (connection.getWidget())
        self.addItem(connection.getWidget())

    def OnNodeConnectionRemoved(self, connection: NodeConnection) -> None:
        assert (connection)
        assert (connection.getWidget())
        self.removeItem(connection.getWidget())
