from __future__ import annotations
from typing import Type
from PySide6.QtWidgets import QWidget, QListWidget, QVBoxLayout

from .asserts import assertRef, assertTrue
from .node import Node


class NodePaletteWidget(QWidget):
    """
    Class defintion for a widget that acts as a node palette allowing users drag and drop 
    different node types into the graph.
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.list_widget: QListWidget = QListWidget(self)
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
        print(f"Updating palette widget with {len(self.__palette_items)} nodes.")
        for item in self.__palette_items:
            self.list_widget.addItem(item.label)
        self.updateGeometry()
