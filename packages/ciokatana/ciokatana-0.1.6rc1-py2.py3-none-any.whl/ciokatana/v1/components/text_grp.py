from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from ciokatana.v1.components import widgets


class TextGrp(QWidget):
    def __init__(self, **kwargs):
        super(TextGrp, self).__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(widgets.FormLabel(kwargs.get("label", "")))

        self.text = QLabel()

        layout.addWidget(self.text)
