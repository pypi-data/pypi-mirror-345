from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QCheckBox, QSpinBox, QLabel


from ciokatana.v1.components import widgets
from ciokatana.v1 import const as k


class IntFieldGrp(QWidget):
    def __init__(self, **kwargs):
        super(IntFieldGrp, self).__init__()

        self.field_label = None
        self.hidable = kwargs.get("hidable")
        self.enablable = kwargs.get("enablable")
        if self.hidable:
            self.enablable = False

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

        field_label_text = kwargs.get("field_label")
        if field_label_text:
            self.field_label = QLabel()
            self.field_label.setStyleSheet(widgets.LABEL_STYLESHEET)
            self.field_label.setText(field_label_text)
            self.field_label.setFixedWidth(80)
            self.field_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
            self.field_label.setIndent(5)
            layout.addWidget(self.field_label)

        # field
        self.field = QSpinBox()
        if kwargs.get("minimum") is not None:
            self.field.setMinimum(kwargs.get("minimum"))
        if kwargs.get("maximum") is not None:
            self.field.setMaximum(kwargs.get("maximum"))

        self.field.setSingleStep(kwargs.get("step", 1))
        self.field.setValue(kwargs.get("default", 0))
        layout.addWidget(self.field)

 
    def set_active(self, value=None):
        if not (self.hidable or self.enablable):
            return
        if self.hidable:
            self._show() if value else self._hide()

        self._enable() if value else self._disable()

    def _hide(self):
        self.display_checkbox.setCheckState(QtCore.Qt.Unchecked)
        self.field.hide()
        if self.field_label:
            self.field_label.hide()

    def _show(self):
        self.display_checkbox.setCheckState(QtCore.Qt.Checked)
        self.field.show()
        if self.field_label:
            self.field_label.show()

    def _disable(self):
        self.display_checkbox.setCheckState(QtCore.Qt.Unchecked)
        self.field.setEnabled(False)
        if self.field_label:
            self.field_label.setEnabled(False)

    def _enable(self):
        self.display_checkbox.setCheckState(QtCore.Qt.Checked)
        self.field.setEnabled(True)
        if self.field_label:
            self.field_label.setEnabled(True)
