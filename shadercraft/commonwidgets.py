import sys
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QSizePolicy,
    QWidget,
    QLabel,
    QLineEdit,
    QDoubleSpinBox,
    QVBoxLayout,
    QHBoxLayout,
    QFrame
)

from .asserts import assertRef, assertTrue, assertType
from .vectors import Vec3F


class CommonWidget(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent=parent)


class TextProperty(CommonWidget):
    """
    Widget that exposes text field to the user along with a label
    """
    text_changed: Signal = Signal(QWidget, str)

    def __init__(self, label: str, parent: QWidget = None) -> None:
        super().__init__(parent=parent)
        self.property_label: str = label

        self.setObjectName("TextProperty")
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setMinimumHeight(46)
        self.setMaximumHeight(self.minimumHeight())

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(2, 2, 2, 2)
        self.layout().setSpacing(0)
        self.frame_widget: QFrame = QFrame(parent=self)
        self.frame_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.frame_widget.setLayout(QVBoxLayout())
        self.frame_widget.layout().setContentsMargins(0, 0, 0, 0)
        self.frame_widget.layout().setSpacing(4)
        self.label_widget: QLabel = QLabel(self.property_label, parent=self.frame_widget)
        self.text_widget: QLineEdit = QLineEdit(parent=self.frame_widget)
        self.text_widget.textChanged.connect(self.onTextChanged)

        self.layout().addWidget(self.frame_widget)
        self.frame_widget.layout().addWidget(self.label_widget)
        self.frame_widget.layout().addWidget(self.text_widget)

    def onTextChanged(self, text: str) -> None:
        """Event handler invoked when the inner text widget changes its text value"""
        self.text_changed.emit(self, text)

    def getTextValue(self) -> str:
        """Get text value from the inner text widget"""
        return self.text_widget.text()

    def setTextValue(self, text: str) -> None:
        """Set text value of the inner text widget"""
        assertType(text, str)
        self.text_widget.setText(text)

    def setReadOnly(self, readonly: bool) -> None:
        """Set value indicating if the inner text widget is editable"""
        self.text_widget.setReadOnly(readonly)


class FloatProperty(CommonWidget):
    """
    Widget that exposes the float field to the user along with a label.
    """
    value_changed: Signal = Signal(QWidget, float)

    def __init__(self, label: str, parent: QWidget = None) -> None:
        super().__init__(parent=parent)
        self.property_label: str = label

        self.setObjectName("TextProperty")
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setMinimumHeight(60)
        self.setMaximumHeight(self.minimumHeight())

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(2, 2, 2, 2)
        self.layout().setSpacing(0)
        self.frame_widget: QFrame = QFrame(parent=self)
        self.frame_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.frame_widget.setLayout(QVBoxLayout())
        self.frame_widget.layout().setContentsMargins(0, 0, 0, 0)
        self.frame_widget.layout().setSpacing(4)
        self.label_widget: QLabel = QLabel(self.property_label, parent=self.frame_widget)
        self.float_widget: QDoubleSpinBox = QDoubleSpinBox(parent=self.frame_widget)
        self.float_widget.setRange(-sys.float_info.max, sys.float_info.max)
        self.float_widget.valueChanged.connect(self.onValueChanged)

        self.layout().addWidget(self.frame_widget)
        self.frame_widget.layout().addWidget(self.label_widget)
        self.frame_widget.layout().addWidget(self.float_widget)

    def onValueChanged(self, value: float) -> None:
        """Event handler invoked when the inner float widget changes its value"""
        self.value_changed.emit(self, value)

    def getValue(self) -> float:
        """Get float value from the inner float widget"""
        return self.float_widget.value()

    def setValue(self, value: float) -> None:
        """Set float value of inner float widget"""
        assertType(value, float)
        self.float_widget.setValue(value)

    def setReadOnly(self, readonly: bool) -> None:
        """Set value indicating if the inner float widget is editable"""
        self.float_widget.setReadOnly(readonly)


class Float3Property(CommonWidget):
    """
    Widget that exposes three float fields (x,y,z) to the user.
    """

    value_changed: Signal = Signal(QWidget, Vec3F)

    def __init__(self, label: str, parent: QWidget = None):
        super().__init__(parent=parent)
        self.property_label: str = label

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(2, 2, 2, 2)
        self.layout().setSpacing(0)
        self.frame_widget: QFrame = QFrame(parent=self)
        self.frame_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        self.frame_widget.setLayout(QVBoxLayout())
        self.frame_widget.layout().setContentsMargins(0, 0, 0, 0)
        self.frame_widget.layout().setSpacing(4)
        self.layout().addWidget(self.frame_widget)

        self.label_widget: QLabel = QLabel(self.property_label, parent=self.frame_widget)
        self.frame_widget.layout().addWidget(self.label_widget)

        self.float_frame: QFrame = QFrame(parent=self.frame_widget)
        self.frame_widget.layout().addWidget(self.float_frame)

        self.float_frame.setLayout(QHBoxLayout())

        self.floatx_widget: QDoubleSpinBox = QDoubleSpinBox(parent=self.float_frame)
        self.floaty_widget: QDoubleSpinBox = QDoubleSpinBox(parent=self.float_frame)
        self.floatz_widget: QDoubleSpinBox = QDoubleSpinBox(parent=self.float_frame)
        self.float_frame.layout().addWidget(self.floatx_widget)
        self.float_frame.layout().addWidget(self.floaty_widget)
        self.float_frame.layout().addWidget(self.floatz_widget)

        self.floatx_widget.valueChanged.connect(self.onValueChanged)
        self.floaty_widget.valueChanged.connect(self.onValueChanged)
        self.floatz_widget.valueChanged.connect(self.onValueChanged)

    def onValueChanged(self, value: float) -> None:
        """
        Event handler invoked when value changes inside any of the three float fields.
        """
        assertType(value, float)
        self.value_changed.emit(self, self.getValue())

    def getValue(self) -> Vec3F:
        """
        Get float values in a form of a list.
        """
        x: float = self.floatx_widget.value()
        y: float = self.floaty_widget.value()
        z: float = self.floatz_widget.value()

        assertType(x, float)
        assertType(y, float)
        assertType(z, float)

        return Vec3F(x, y, z)

    def setValue(self, value: Vec3F) -> None:
        """
        Set float value.
        """
        assertType(value, Vec3F)
        self.floatx_widget.setValue(value.x)
        self.floaty_widget.setValue(value.y)
        self.floatz_widget.setValue(value.z)

    def setReadOnly(self, readonly: bool) -> None:
        """
        Set value indicating if the float fields are editable or not.
        """
        self.floatx_widget.setReadOnly(readonly)
        self.floaty_widget.setReadOnly(readonly)
        self.floatz_widget.setReadOnly(readonly)
