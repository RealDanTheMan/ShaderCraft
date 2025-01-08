from typing import Optional
from uuid import UUID
import logging as Log
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QSizePolicy,
    QWidget, 
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton
)

from .asserts import assertRef, assertTrue
from .node import Node

class PropertyPanelWidget(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent=parent)
        self.__active_node: Optional[Node] = None

        self.setObjectName("PropertyPanelWidget")
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(6, 2, 6, 2)
        self.layout().setSpacing(0)

        self._initGeneralPropertyWidgets()
        self._initInputPropertyWidgets()

    def _initGeneralPropertyWidgets(self) -> None:
        """
        Creates & sets up the general node property portion of the panel.
        General properties are static properties that every node contains.
        """
        self.general_box: QGroupBox = QGroupBox("General Properties", parent=self)
        self.general_box.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.general_box.setCheckable(False)
        self.general_box.setChecked(False)
        self.layout().addWidget(self.general_box)

        self.general_box.setLayout(QVBoxLayout())
        self.general_box.layout().setContentsMargins(0, 0, 0, 10)
        self.general_box.layout().setSpacing(10)
        self.type_property: PropertyWidget = PropertyWidget(
            "Node Type",
            str,
            parent=self.general_box
        )

        self.name_property: PropertyWidget = PropertyWidget(
            "Node Name",
            str,
            parent=self.general_box
        )

        self.uuid_property: PropertyWidget = PropertyWidget(
            "Node UUID",
            UUID,
            parent=self.general_box
        )

        self.positionx_property: PropertyWidget = PropertyWidget(
            "Position X",
            float,
            parent=self.general_box
        )

        self.positiony_property: PropertyWidget = PropertyWidget(
            "Position Y",
            float,
            parent=self.general_box
        )

        self.general_box.layout().addWidget(self.name_property)
        self.general_box.layout().addWidget(self.type_property)
        self.general_box.layout().addWidget(self.uuid_property)
        self.general_box.layout().addWidget(self.positionx_property)
        self.general_box.layout().addWidget(self.positiony_property)

    def _initInputPropertyWidgets(self) -> None:
        """
        Creates & sets up node input property protion of the panel.
        Input properties are dynamic and depend on node type.
        """
        self.input_properties_box: QGroupBox = QGroupBox("Input Properties", parent=self)
        self.input_properties_box.setCheckable(False)
        self.input_properties_box.setChecked(False)
        self.input_properties_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.layout().addWidget(self.input_properties_box)

    def setActiveNode(self, node: Node) -> None:
        """Set active node bound to this property panel"""
        Log.debug(f"Setting property panel active node -> {node}")
        self.__active_node = node

    def getActiveNode(self) -> Optional[Node]:
        """Get active node bound to this property panel"""
        return self.__active_node

    def fetchNodeValues(self):
        node: Node = self.getActiveNode()
        if node is None:
            return

        Log.info("Fetching active node property panel values")
        self.type_property.setValue(node.label)
        self.name_property.setValue(node.name)
        self.uuid_property.setValue(node.uuid)
        self.positionx_property.setValue(node.posx)
        self.positiony_property.setValue(node.posy)


class PropertyWidget(QWidget):
    def __init__(self, label: str, property_type: type, parent: QWidget = None) -> None:
        super().__init__(parent=parent)
        self.property_label: str = label
        self.property_type: type = property_type
        self.property_value: object = None

        self.setObjectName("PropertyWidget")
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(2, 2, 2, 2)
        self.layout().setSpacing(0)
        self.frame_widget: QFrame = QFrame(parent=self)
        self.frame_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.frame_widget.setLayout(QVBoxLayout())
        self.frame_widget.layout().setContentsMargins(0, 0, 0, 0)
        self.frame_widget.layout().setSpacing(4)
        self.label_widget: QLabel = QLabel(self.property_label, parent=self.frame_widget)
        self.value_widget: QLineEdit = QLineEdit(parent=self.frame_widget)

        self.layout().addWidget(self.frame_widget)
        self.frame_widget.layout().addWidget(self.label_widget)
        self.frame_widget.layout().addWidget(self.value_widget)

    def getValue(self) -> object:
        """Get property widget value"""
        return None

    def setValue(self, value: object) -> None:
        """Set property widget value"""
        assertRef(value)
        assertTrue(isinstance(value, self.property_type))
        self.property_value = value
        self.value_widget.setText(str(value))
