from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel

from ciokatana.v1 import const as k

TEXT_COLOR = "#757575"
LABEL_STYLESHEET = "QLabel {{color: {}; }}".format(TEXT_COLOR)
CHECKBOX_STYLESHEET = "QCheckBox {{color: {}; }}".format(TEXT_COLOR)


class FormLabel(QLabel):
    def __init__(self, label, tooltip=None):
        super(FormLabel, self).__init__()

        self.setText(label)
        self.setFixedWidth(170)
        self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self.setIndent(5)
        self.setStyleSheet(LABEL_STYLESHEET)

        if tooltip:
            tooltip = tooltip.replace("\n\n", "<br>")
            tooltip = f"<b>{label}</b><br>{tooltip}"
            self.setToolTip(tooltip)
