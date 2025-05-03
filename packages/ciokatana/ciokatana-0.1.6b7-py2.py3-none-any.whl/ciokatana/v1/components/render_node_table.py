from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt
from Katana import NodegraphAPI

import weakref

OVERRIDE_SQUARE = 10
BLUE = QColor(0, 100, 140)
GREY = QColor(80, 80, 80)

HEADER_STYLESHEET = """
QLabel {
    color: #757575;
    border: 1px solid #444;
    border-top-style:none;
    border-right-style:none;
    border-left-style:none;
    }
"""

CONTENT_STYLESHEET = """
QLabel {
    color: #aaa;
    border: 1px solid #444;
    border-top-style:none;
    border-right-style:none;
    border-left-style:none;
    }
"""
# Content row looks a little different when it represents an override
CONTENT_OVERRIDE_STYLESHEET = """
QLabel {
    color: #89f;
    font-weight: bold;
    border: 1px solid #444;
    border-top-style:none;
    border-right-style:none;
    border-left-style:none;
    }
"""


# A little square to represent whether or not the render node has overrides
class OverrideIndicator(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    def paintEvent(self, event):
        ystart = (self.height() - OVERRIDE_SQUARE) * 0.5

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(BLUE)
        if not self.isEnabled():
            painter.setBrush(GREY)
        painter.drawRect(0, ystart, OVERRIDE_SQUARE, OVERRIDE_SQUARE)


class RenderNodeRow(QWidget):
    """Base class for a row"""

    STYLESHEET = None

    def __init__(self):
        super(RenderNodeRow, self).__init__()
        self.row_layout = QHBoxLayout()
        self.row_layout.setAlignment(Qt.AlignHCenter)
        self.row_layout.setContentsMargins(20, 0, 20, 0)

        self.override_widget = None
        self.render_node_widget = None
        self.frame_spec_widget = None
        self.scout_spec_widget = None
        self.chunk_size_widget = None
        self.select_button_widget = None

    def build_ui(self):
        """Configure the widgets"""
        # Config
        self.override_widget.setFixedWidth(30)
        self.render_node_widget.setMinimumWidth(100)
        self.frame_spec_widget.setMinimumWidth(90)
        self.scout_spec_widget.setMinimumWidth(60)
        self.chunk_size_widget.setMinimumWidth(50)
        self.select_button_widget.setFixedWidth(80)

        self.render_node_widget.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.frame_spec_widget.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.scout_spec_widget.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.chunk_size_widget.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.set_style_sheet(self.STYLESHEET)

        # Add the widgets to the row layout
        self.row_layout.addWidget(self.override_widget)
        self.row_layout.addWidget(self.render_node_widget, 2)
        self.row_layout.addWidget(self.frame_spec_widget, 2)
        self.row_layout.addWidget(self.scout_spec_widget, 2)
        self.row_layout.addWidget(self.chunk_size_widget, 1)
        self.row_layout.addWidget(self.select_button_widget)
        self.setLayout(self.row_layout)

    def set_style_sheet(self, style_sheet):
        self.render_node_widget.setStyleSheet(style_sheet)
        self.frame_spec_widget.setStyleSheet(style_sheet)
        self.scout_spec_widget.setStyleSheet(style_sheet)
        self.chunk_size_widget.setStyleSheet(style_sheet)


class RenderNodeHeaderRow(RenderNodeRow):
    """The header row. Inherits layout from RenderNodeRow"""

    STYLESHEET = HEADER_STYLESHEET

    def __init__(self):
        super(RenderNodeHeaderRow, self).__init__()

        self.render_node_widget = QLabel("Render node")
        self.frame_spec_widget = QLabel("Frame spec")
        self.scout_spec_widget = QLabel("Scout spec")
        self.chunk_size_widget = QLabel("Chunk size")
        self.override_widget = QLabel()
        self.select_button_widget = QLabel()

        self.build_ui()


class RenderNodeContentRow(RenderNodeRow):
    """A row containing render node information.

    Inherits layout from RenderNodeRow
    """

    STYLESHEET = CONTENT_STYLESHEET

    def __init__(self):
        super(RenderNodeContentRow, self).__init__()

        self.willBeRemoved = False
        row_layout = QHBoxLayout()
        row_layout.setAlignment(Qt.AlignLeft)

        # Create and add the widgets to the row layout
        self.override_widget = OverrideIndicator()
        self.render_node_widget = QLabel()
        self.frame_spec_widget = QLabel()
        self.scout_spec_widget = QLabel()
        self.chunk_size_widget = QLabel()
        self.select_button_widget = QPushButton("Editor")

        self.build_ui()

        # Extra config
        self.select_button_widget.setFixedHeight(20)
        self.select_button_widget.setAutoDefault(False)
        self.select_button_widget.clicked.connect(self.set_edited)

    def hydrate(self, data):
        """Set the data for the row."""
        self.render_node_widget.setText(data["render_node"].getName())
        self.frame_spec_widget.setText(data["frame_spec"])
        self.scout_spec_widget.setText(data["scout_spec"])
        self.chunk_size_widget.setText(str(data["chunk_size"]))
        self.override_widget.setEnabled(int(data["do_override"]))
        if data["do_override"]:
            self.set_style_sheet(CONTENT_OVERRIDE_STYLESHEET)
        else:
            self.set_style_sheet(CONTENT_STYLESHEET)

    def set_edited(self):
        """Show the render node in the parameters pane."""
        render_node = NodegraphAPI.GetNode(self.render_node_widget.text())
        NodegraphAPI.SetNodeEdited(render_node, True, True)


class RenderNodeTable(QWidget):
    """Manage the list of render nodes
    """

    def __init__(self):
        super(RenderNodeTable, self).__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        header_row = RenderNodeHeaderRow()
        self.layout.addWidget(header_row)
        self.content_layout = QVBoxLayout()
        self.layout.addLayout(self.content_layout)
        self.content_layout.setAlignment(Qt.AlignTop)


    def set_entries(self, entries):
        """Set the list of render node entries.

        1. Adjust the number of rows to match the number of entries.
        2. Hydrate each row.
        """
        num_children = self.content_layout.count()
        num_entries = len(entries)
        difference = num_entries - num_children
        if difference > 0:
            for i in range(difference):
                entry = RenderNodeContentRow()
                self.content_layout.addWidget(entry)
        elif difference < 0:  # remove extra widgets
            first = num_children - num_entries
            for i in range(first, num_children):
                self.content_layout.itemAt(i).widget().willBeRemoved = True
            self.purge_extras()

        for i, entry in enumerate(entries):
            widget = self.content_layout.itemAt(i).widget()
            widget.hydrate(entry)

    def hydrate_entry(self, index, entry):
        """Set the data and style for a single row."""
        self.content_layout.itemAt(index).widget().hydrate(entry)

    def clear(self):
        """Flag all rows for deletion and calls purge."""
        for i in range(self.content_layout.count()):
            self.content_layout.itemAt(i).widget().willBeRemoved = True
            self.purge_extras()

    def purge_extras(self):
        """Remove all flagged rows."""
        for i in range(self.content_layout.count()):
            widget = self.content_layout.itemAt(i).widget()
            if widget.willBeRemoved:
                self.content_layout.removeWidget(widget)
                widget.deleteLater()
                widget = None
