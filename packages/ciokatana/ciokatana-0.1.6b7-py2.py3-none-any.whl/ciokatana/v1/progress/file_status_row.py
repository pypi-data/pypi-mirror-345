from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QFrame,
)
from PyQt5.QtCore import Qt

from ciokatana.v1 import const as k

CHIP_HEIGHT = 20

ROUNDED_LEFT = (
    "border-radius: 0; border-top-left-radius: 3px; border-bottom-left-radius: 3px"
)
ROUNDED_RIGHT = (
    "border-radius: 0; border-top-right-radius: 3px; border-bottom-right-radius: 3px"
)

RIBBON_STYLESHEET = {
    "OFF": f"background-color: {k.OFF_GRADIENT};{ROUNDED_LEFT};",
    "MD5_COMPLETE": f"background-color: {k.MD5_GRADIENT};{ROUNDED_LEFT};",
    "MD5_CACHED": f"background-color: {k.MD5_CACHE_GRADIENT};{ROUNDED_LEFT};",
}

PROGRESS_BAR_STYLESHEET = f"""
QProgressBar {{
    background-color: {k.OFF_GRADIENT};
    font-size: 12px;
    {ROUNDED_RIGHT};
}} 
QProgressBar::chunk {{
    background-color: {k.UPLOAD_GRADIENT};
}}
"""

PROGRESS_BAR_STYLESHEET_ALREADY_UPLOADED = f"""
QProgressBar {{
    background-color: {k.OFF_GRADIENT};
    font-size: 12px;
    {ROUNDED_RIGHT};
}}
QProgressBar::chunk {{
    background-color: {k.UPLOAD_CACHE_GRADIENT};
}}
"""


class FileStatusRow(QWidget):
    def __init__(self, filename, *args, **kwargs):
        super(FileStatusRow, self).__init__(*args, **kwargs)

        self.layout = QHBoxLayout()

        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(0)

        self.setLayout(self.layout)
        self.filename_label = QLabel(filename)
        self.filename_label.setContentsMargins(0, 0, 10, 0)
        self.status_chip = StatusChip()

        self.layout.addWidget(self.filename_label)
        self.layout.addStretch()
        self.layout.addWidget(self.status_chip)


class StatusChip(QFrame):
    def __init__(self, *args, **kwargs):
        super(StatusChip, self).__init__(*args, **kwargs)

        self.setFixedHeight(CHIP_HEIGHT)
        self.setFixedWidth(80)

        layout = QHBoxLayout()
        layout.setSpacing(0)
        self.setLayout(layout)

        self.md5_ribbon = QFrame()
        self.md5_ribbon.setFixedWidth(14)
        self.md5_ribbon.setStyleSheet(RIBBON_STYLESHEET["OFF"])

        self.upload_progress_bar = QProgressBar()
        self.upload_progress_bar.setFixedWidth(64)
        self.upload_progress_bar.setAlignment(Qt.AlignCenter)

        self.upload_progress_bar.setStyleSheet(PROGRESS_BAR_STYLESHEET)
        self.upload_progress_bar.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.md5_ribbon)
        layout.addWidget(self.upload_progress_bar)

        self.progress = {
            "bytes_to_upload": 0,
            "bytes_uploaded": 0,
            "already_uploaded": False,
            "md5": "",
            "md5_was_cached": False,
        }

    def update_status(self, progress):
        self.progress.update(progress)

        if self.progress["md5_was_cached"]:
            md5_stylesheet = RIBBON_STYLESHEET["MD5_CACHED"]
        elif self.progress["md5"]:
            md5_stylesheet = RIBBON_STYLESHEET["MD5_COMPLETE"]
        else:
            md5_stylesheet = RIBBON_STYLESHEET["OFF"]

        self.md5_ribbon.setStyleSheet(md5_stylesheet)

        if self.progress["already_uploaded"]:
            percentage = 100
            progress_bar_stylesheet = PROGRESS_BAR_STYLESHEET_ALREADY_UPLOADED
            self.upload_progress_bar.setFormat("Cached")
        elif self.progress["bytes_to_upload"] == 0:
            percentage = 0
            progress_bar_stylesheet = PROGRESS_BAR_STYLESHEET
        else:
            percentage = int(
                self.progress["bytes_uploaded"] * 100 / self.progress["bytes_to_upload"]
            )
            progress_bar_stylesheet = PROGRESS_BAR_STYLESHEET

        self.upload_progress_bar.setStyleSheet(progress_bar_stylesheet)
        self.upload_progress_bar.setValue(percentage)
