import logging
import os
import re
import hashlib
import time

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)


import UI4

SHA_TRUNCATE = 6
log = logging.getLogger(__name__)


class RenderFilenameDialog(QDialog):
    """
    Save as dialog for the render filename.
    """

    def __init__(self, project_filename):
        QDialog.__init__(self, UI4.App.MainWindow.GetMainWindow())

        self.directory = os.path.dirname(project_filename)
        self.basename, self.ext = os.path.splitext(os.path.basename(project_filename))

        sha = hashlib.sha1(str(time.time()).encode("utf-8")).hexdigest()[:SHA_TRUNCATE]
        basename = re.sub(f"_cio[0-9a-f]{{{SHA_TRUNCATE}}}", "",  self.basename)
        suggested_name = f"{basename}_cio{sha}"

        self.initUI(suggested_name)

    def initUI(self, suggested_name):
        self.setWindowTitle("Save as")

        label = QLabel(
            "You must save the scene so that it can be shipped to Conductor.\nEnter a name below or use the suggested name and hit Save."
        )
        self.text_field = QLineEdit()
        self.text_field.setStyleSheet("QLineEdit { margin: 10px; }")

        self.text_field.setText(suggested_name)
        self.fullpath_label = QLabel()
        cancel_button = QPushButton("Cancel")
        save_button = QPushButton("Save")

        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.text_field)
        layout.addWidget(self.fullpath_label)

        button_layout = QHBoxLayout()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.resolve_full_path()

        self.text_field.textChanged.connect(self.resolve_full_path)

        # Connect button signals to slots
        cancel_button.clicked.connect(self.cancel)
        save_button.clicked.connect(self.save)

    def resolve_full_path(self):
        value = f"{self.directory}/{self.text_field.text()}{self.ext}"
        value = re.sub(r"\\+", "/", value)
        self.fullpath_label.setText(value)

    def cancel(self):
        self.result = None
        self.reject()

    def save(self):
        self.result = self.fullpath_label.text()
        self.accept()


def show_dialog(project_filename):
    dialog = RenderFilenameDialog(project_filename)
    if dialog.exec_() == QDialog.Accepted:
        return dialog.result
    return None
