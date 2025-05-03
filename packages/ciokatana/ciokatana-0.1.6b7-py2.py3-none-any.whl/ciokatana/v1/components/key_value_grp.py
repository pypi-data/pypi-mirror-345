
from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLineEdit, QCheckBox, QVBoxLayout

class KeyValueHeaderGrp(QWidget):
    """A header row"""

    def __init__(self, **kwargs):
        super(KeyValueHeaderGrp, self).__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)
        self.add_button = QPushButton("Add")
        self.add_button.setFixedWidth(60)
        self.add_button.setAutoDefault(False)

        self.key_header = QPushButton(kwargs.get("key_label", "Key"))
        policy = self.key_header.sizePolicy()
        policy.setHorizontalStretch(2)
        self.key_header.setSizePolicy(policy)
        self.key_header.setEnabled(False)
        self.key_header.setAutoDefault(False)

        self.value_header = QPushButton(kwargs.get("value_label", "Value"))
        policy = self.value_header.sizePolicy()
        policy.setHorizontalStretch(3)
        self.value_header.setSizePolicy(policy)
        self.value_header.setEnabled(False)
        self.value_header.setAutoDefault(False)

        layout.addWidget(self.add_button)
        layout.addWidget(self.key_header)
        layout.addWidget(self.value_header)

        if kwargs.get("checkbox_label") is not None:
            self.cb_header = QPushButton(
                kwargs.get("checkbox_label", "Active")
            )
            self.cb_header.setFixedWidth(60)
            self.cb_header.setEnabled(False)
            self.cb_header.setAutoDefault(False)
            layout.addWidget(self.cb_header)
        else:
            layout.addSpacing(65)


class KeyValuePairGrp(QWidget):
    """A single row"""

    delete_pressed = Signal(QWidget)

    def __init__(self, do_checkbox):
        super(KeyValuePairGrp, self).__init__()

        layout = QHBoxLayout()
        self.willBeRemoved = False
        self.checkbox = None
        self.setLayout(layout)
        self.delete_button = QPushButton("X")
        self.delete_button.setFixedWidth(40)
        self.delete_button.setAutoDefault(False)
        self.delete_button.clicked.connect(self.delete_me)

        self.key_field = QLineEdit()
        policy = self.key_field.sizePolicy()
        policy.setHorizontalStretch(2)
        self.key_field.setSizePolicy(policy)

        self.value_field = QLineEdit()
        policy = self.value_field.sizePolicy()
        policy.setHorizontalStretch(3)
        self.value_field.setSizePolicy(policy)

        layout.addWidget(self.delete_button)
        layout.addWidget(self.key_field)
        layout.addWidget(self.value_field)

        if do_checkbox:
            self.checkbox = QCheckBox()
            self.checkbox.setFixedWidth(60)
            layout.addWidget(self.checkbox)
        else:
            layout.addSpacing(65)

    def delete_me(self):
        self.delete_pressed.emit(self)


class KeyValueGrpList(QWidget):
    """The list of KeyValuePairGrps"""

    edited = Signal()

    def __init__(self, **kwargs):
        super(KeyValueGrpList, self).__init__()

        self.has_checkbox = kwargs.get("checkbox_label") is not None

        self.header_component = KeyValueHeaderGrp(**kwargs)
        self.content_layout = QVBoxLayout()
        self.setLayout(self.content_layout)

        self.content_layout.addWidget(self.header_component)

        self.entries_component = QWidget()
        self.entries_layout = QVBoxLayout()
        self.entries_component.setLayout(self.entries_layout)
        self.content_layout.addWidget(self.entries_component)

        self.header_component.add_button.clicked.connect(self.add_entry)

    def set_entries(self, entry_list):
        if self.has_checkbox:
            for row in entry_list:
                self.add_entry(False, key=row[0], value=row[1], check=row[2])
        else:
            for row in entry_list:
                self.add_entry(False, key=row[0], value=row[1])

    def add_entry(self, clicked, key="", value="", check=False):
        entry = KeyValuePairGrp(self.has_checkbox)
        entry.key_field.setText(key)
        entry.value_field.setText(value)
        if self.has_checkbox:
            entry.checkbox.setChecked(check)

        self.entries_layout.addWidget(entry)

        entry.delete_pressed.connect(remove_widget)
        entry.delete_pressed.connect(self.something_changed)
        entry.key_field.editingFinished.connect(self.something_changed)
        entry.value_field.editingFinished.connect(self.something_changed)
        if self.has_checkbox:
            entry.checkbox.stateChanged.connect(self.something_changed)

    def something_changed(self):
        self.edited.emit()

    def entry_widgets(self):
        return [
            e
            for e in self.entries_component.children()
            if e.metaObject().className() == "KeyValuePairGrp" and not e.willBeRemoved
        ]

    def entries(self):
        result = []
        for widget in self.entry_widgets():
            key = widget.key_field.text().strip()
            value = widget.value_field.text().strip()
            if key and value:
                if self.has_checkbox:
                    checked = widget.checkbox.isChecked()
                    result.append([key, value, checked])
                else:
                    result.append([key, value])
        return result

    def clear(self):
        for entry in self.entries():
            remove_widget(entry)


@Slot(QWidget)
def remove_widget(widget):
    # Since the widget is not deleted immediately, KeyValueGrpList.entries()
    # will return the entry in the deleted widget as well. By setting a flag:
    # willBeRemoved, we can check it in KeyValueGrpList.entry_widgets() and then
    # ignore unwanted widgets when persisting entries to some store.
    widget.willBeRemoved = True
    widget.layout().removeWidget(widget)
    widget.deleteLater()
