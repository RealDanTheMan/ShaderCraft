from typing import Optional
from uuid import UUID
import logging as Log
from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import (
    QSizePolicy,
    QWidget, 
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QFrame,
    QLabel,
    QLineEdit,
    QDoubleSpinBox
)

from .asserts import assertRef, assertTrue, assertType
from .node import Node
from .commonwidgets import TextProperty, FloatProperty

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

        self.type_property: TextProperty = TextProperty("Node Type", parent=self.general_box)
        self.name_property: TextProperty = TextProperty("Node Name", parent=self.general_box)
        self.uuid_property: TextProperty = TextProperty("Node UUID", parent=self.general_box)

        self.positionx_property: FloatProperty = FloatProperty(
            "Position X",
            parent=self.general_box
        )

        self.positiony_property: FloatProperty = FloatProperty(
            "Position Y",
            parent=self.general_box
        )

        self.name_property.setReadOnly(True)
        self.type_property.setReadOnly(True)
        self.uuid_property.setReadOnly(True)
        self.positionx_property.value_changed.connect(self.onGeneralPropertyValueChanged)
        self.positiony_property.value_changed.connect(self.onGeneralPropertyValueChanged)

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
        self.type_property.setTextValue(node.label)
        self.name_property.setTextValue(node.name)
        self.uuid_property.setTextValue(str(node.uuid))
        self.positionx_property.setValue(node.posx)
        self.positiony_property.setValue(node.posy)

    def onGeneralPropertyValueChanged(self, widget: QWidget, value: object) -> None:
        if self.__active_node is None:
            return

        print(f"Property panel property changed -> {widget} = {value}")

        if widget == self.positionx_property:
            self.__active_node.setPosition(value, self.__active_node.posy)
            return

        if widget == self.positiony_property:
            self.__active_node.setPosition(self.__active_node.posx, value)
            return
