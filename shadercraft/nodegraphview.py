from __future__ import annotations
from typing import Optional
from PySide6.QtWidgets import QGraphicsView


class NodeGraphView(QGraphicsView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
