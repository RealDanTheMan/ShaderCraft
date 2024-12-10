from .node_widget import NodeWidget


class Node(object):
    def __init__(self):
        self.label: str = "Node Label"
        self.name: str = "Node Name"
        self.guid: int = 0
        self.widget: None

    def initWidget(self):
        self.widget = NodeWidget()
        self.widget.setLabelText(self.label)

    def getWidget(self) -> NodeWidget:
        return self.widget
