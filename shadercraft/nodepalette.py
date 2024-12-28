from __future__ import annotations
from typing import Type
from dataclasses import dataclass
from PySide6.QtWidgets import QWidget, QListWidget, QListWidgetItem, QVBoxLayout
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QMouseEvent

from .asserts import assertRef, assertTrue
from .node import Node, NodeClassDesc


class NodeListWidget(QListWidget):
    """
    Widget class for representing custom list containing node palette items
    Users can pick nodes from the palette and drop them into the graphs.
    """
    itemDoubleClicked = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Event handler invoked when user performs mouse double click over of the list items"""
        item = self.itemAt(event.pos())
        if item is not None:
            self.itemDoubleClicked.emit(item)
            return
        super().mouseDoubleClickEvent(event)


class NodePaletteWidget(QWidget):
    """
    Class defintion for a widget that acts as a node palette allowing users drag and drop 
    different node types into the graph.
    """
    createNodeRequested = Signal(NodeClassDesc)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.list_widget: NodeListWidget = NodeListWidget(self)
        self.list_widget.itemDoubleClicked.connect(self.onListItemDoubleClicked)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(2, 2, 2, 2)
        self.layout().setSpacing(0)
        self.layout().addWidget(self.list_widget)

        self.__palette_items: list[Type[Node]] = []

    def clear(self) -> None:
        """Clears all items from the palette list"""
        assertRef(self.list_widget)
        self.list_widget.clear()
        self.__palette_items.clear()

    def addPaletteItem(self, item: Type[Node]) -> None:
        """Adds node type as an item to the palette list"""
        assertTrue(item not in self.__palette_items)
        self.__palette_items.append(item)

    def addPaletteItems(self, items: list[Type[Node]]) -> None:
        """Adds list of node types as items into the palette list"""
        for item in items:
            self.addPaletteItem(item)

    def refresh(self) -> None:
        """Updates the widget and rebuilds the palette item list"""
        assertRef(self.list_widget)
        for item in self.__palette_items:
            list_item: QListWidgetItem = QListWidgetItem(item.label)
            list_item.setData(Qt.UserRole, NodeClassDesc.fromNodeClass(item))
            self.list_widget.addItem(list_item)
        self.updateGeometry()

    def onListItemDoubleClicked(self, item) -> None:
        """Event handler invoked when the item on palette list widget receives double mouse click"""
        assertRef(item)
        data = item.data(Qt.UserRole)
        if data is not None and isinstance(data, NodeClassDesc):
            self.createNodeRequested.emit(data)
