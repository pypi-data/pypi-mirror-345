
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QCheckBox

from ciokatana.v1.components import widgets
from ciokatana.v1 import const as k

class CheckboxGrp(QWidget):

    def __init__(self, **kwargs):
        super(CheckboxGrp, self).__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)
        num_checkboxes = kwargs.get("checkboxes", 1)
        sublabels = kwargs.get("sublabels", [])

        if len(sublabels) != num_checkboxes:
            sublabels = [""] * num_checkboxes

        layout.addWidget(widgets.FormLabel(kwargs.get("label", "")))

        self.checkboxes = []

        for i in range(num_checkboxes):
            cb = QCheckBox(sublabels[i])
            cb.setStyleSheet(widgets.CHECKBOX_STYLESHEET)
            self.checkboxes.append(cb)
            layout.addWidget(cb)