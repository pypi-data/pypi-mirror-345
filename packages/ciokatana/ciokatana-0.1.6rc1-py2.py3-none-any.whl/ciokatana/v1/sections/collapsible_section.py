from PyQt5 import QtCore
from PyQt5.QtWidgets import QFrame, QToolButton, QSizePolicy, QToolBar, QWidget, QVBoxLayout

from ciokatana.v1.model import collapsible_panel_model

EXPANDED_STYLESHEET = (
    "CollapsibleSection { border: 1px solid #383838; border-radius: 5px;}"
)
COLLAPSED_STYLESHEET = "CollapsibleSection { border: none;}"

TOGGLE_BUTTON_STYLESHEET = """
QToolButton { 
border: none; 
color: #a8a8a8; 
font-weight: normal; 
background-color: #383838; 
border-top-left-radius: 5px;
border-top-right-radius: 5px; 
}
"""

TOOLBAR_STYLESHEET = """
QToolBar {
    border: none;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    }
"""


class CollapsibleSection(QFrame):
    """Base class for collapsible sections.

    A collapsible section is a section that can be collapsed or expanded by
    clicking the title.

    Handle common initialization, and provide some methods to be implemented in
    subclasses.
    """

    def __init__(self, editor, title):
        super(CollapsibleSection, self).__init__()

        self.editor = editor
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_area.setLayout(self.content_layout)

        toolbar = QToolBar()
        self.toggle_button = QToolButton()

        self._configure_toggle_button(title)
        toolbar.addWidget(self.toggle_button)
        toolbar.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Maximum
        )
        toolbar.setFixedHeight(20)

        toolbar.setStyleSheet(TOOLBAR_STYLESHEET)

        self.content_area.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Maximum
        )

        layout = QVBoxLayout()

        layout.addWidget(toolbar)
        layout.addWidget(self.content_area)
        self.setLayout(layout)

        self.toggle_button.clicked.connect(self.on_toggle)
        self.toggle_button.clicked.connect(self.set_expanded)

    def on_toggle(self, expand):
        self.toggle_button.setChecked(expand)
        # persist
        collapsible_panel_model.set_section_state(
            self.editor.node, expand, self.__class__.__name__
        )

    def set_expanded(self, expand):
        if expand:
            self.toggle_button.setArrowType(QtCore.Qt.DownArrow)
            self.content_area.show()
            self.setStyleSheet(EXPANDED_STYLESHEET)
        else:
            self.toggle_button.setArrowType(QtCore.Qt.RightArrow)
            self.content_area.hide()
            self.setStyleSheet(COLLAPSED_STYLESHEET)

    def hydrate(self):
        """Set the collapsed state based on the last saved state from the node."""
        expanded = collapsible_panel_model.get_section_state(
            self.editor.node, self.__class__.__name__
        )
        self.set_expanded(expanded)
        self.toggle_button.setChecked(int(expanded))

    # PRIVATE
    def _configure_toggle_button(self, title):
        self.toggle_button.setStyleSheet(TOGGLE_BUTTON_STYLESHEET)
        self.toggle_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setText(title)
        self.toggle_button.setIconSize(QtCore.QSize(2, 2))
        self.toggle_button.setCheckable(True)
        self.toggle_button.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Maximum
        )

    def add_separator(self):
        separator = QFrame()
        separator.setLineWidth(1)
        separator.setFrameStyle(QFrame.HLine | QFrame.Raised)
        self.content_layout.addWidget(separator)
