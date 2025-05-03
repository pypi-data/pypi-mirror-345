from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QCheckBox, QLineEdit
from ciokatana.v1.components import widgets
from ciokatana.v1 import const as k


class TextFieldGrp(QWidget):
    def __init__(self, **kwargs):
        super(TextFieldGrp, self).__init__()

        self.hidable = kwargs.get("hidable")
        self.enablable = kwargs.get("enablable")
        self.display_checkbox = None

        if self.hidable:
            self.enablable = False

        placeholder = kwargs.get("placeholder")

        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(
            widgets.FormLabel(kwargs.get("label", ""), tooltip=kwargs.get("tooltip"))
        )

        # hidable checkbox
        if self.hidable or self.enablable:
            self.display_checkbox = QCheckBox()
            layout.addWidget(self.display_checkbox)
            self.display_checkbox.stateChanged.connect(self.set_active)

        # field
        self.field = QLineEdit()
        layout.addWidget(self.field)
        if placeholder:
            self.field.setPlaceholderText(placeholder)

    def set_active(self, value=None):
        if not (self.hidable or self.enablable):
            return
        if self.hidable:
            self._show() if value else self._hide()

        self._enable() if value else self._disable()

    # TODO - Put all the extras in a widget and show/hide/enable/disable the widget
    def _hide(self):
        self.display_checkbox.setCheckState(QtCore.Qt.Unchecked)
        self.field.hide()

    def _show(self):
        self.display_checkbox.setCheckState(QtCore.Qt.Checked)
        self.field.show()

    def _disable(self):
        self.display_checkbox.setCheckState(QtCore.Qt.Unchecked)
        self.field.setEnabled(False)

    def _enable(self):
        self.display_checkbox.setCheckState(QtCore.Qt.Checked)
        self.field.setEnabled(True)
