from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from ciokatana.v1.Node import ConductorRenderNode
from ciokatana.v1.Panel import ConductorRenderPanel


class ConductorRenderEditor(QWidget):
    """
    Encapsulate the ConductorRenderPanel in the parameters editor.
    """
    def __init__(self, parent, node):
        QWidget.__init__(self, parent)

        # Ensure projects, instance types, and packages are valid
        ConductorRenderNode.connect()

        self.setFixedHeight(1200)
        self.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Maximum
        )
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.panel = ConductorRenderPanel(self, node)
        self.layout.addWidget(self.panel)
