from PyQt5.QtWidgets import (
    QListWidget,
    QAbstractItemView,
    QPushButton,
    QHBoxLayout,
    QFileDialog,
)
from ciokatana.v1.sections.collapsible_section import CollapsibleSection
from ciokatana.v1.model import assets_model
from ciopath.gpath_list import PathList


class AssetsSection(CollapsibleSection):
    """Manage asset collection and upload parameters.

    This section consists of buttons to browse for assets, and a list widget to
    display them. There's also a checkbox to enable/disable the upload daemon.
    """

    ORDER = 65

    def __init__(self, editor):
        super(AssetsSection, self).__init__(editor, "Extra Assets")

        # Buttons
        self.button_layout = QHBoxLayout()

        for button in [
            {"label": "Clear", "func": self.clear},
            {"label": "Remove selected", "func": self.remove_selected},
            {"label": "Browse files", "func": self.browse_files},
            {"label": "Browse directory", "func": self.browse_dir},
        ]:
            btn = QPushButton(button["label"])
            btn.setAutoDefault(False)
            btn.clicked.connect(button["func"])
            self.button_layout.addWidget(btn)

        self.content_layout.addLayout(self.button_layout)

        # List
        self.list_component = QListWidget()
        self.list_component.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_component.setFixedHeight(140)
        self.content_layout.addWidget(self.list_component)

    def add_paths(self, *paths):
        # use a PathList to deduplicate.
        path_list = PathList(*self.entries())
        path_list.add(*paths)
        self.list_component.clear()
        self.list_component.addItems([p.fslash() for p in path_list])

    def entries(self):
        result = []
        for i in range(self.list_component.count()):
            result.append(self.list_component.item(i).text())
        return result

    def clear(self):
        self.list_component.clear()
        assets_model.set_entries(self.editor.node, [])

    def remove_selected(self):
        model = self.list_component.model()
        for row in sorted(
            [
                index.row()
                for index in self.list_component.selectionModel().selectedIndexes()
            ],
            reverse=True,
        ):
            model.removeRow(row)
        self.persist_entries()

    def browse_files(self):
        result = QFileDialog.getOpenFileNames(
            parent=None, caption="Select files to upload"
        )
        if len(result) and len(result[0]):
            self.add_paths(*result[0])
            self.persist_entries()

    def browse_dir(self):
        result = QFileDialog.getExistingDirectory(
            parent=None, caption="Select a directory to upload"
        )
        if result:
            self.add_paths(result)
            self.persist_entries()

    def persist_entries(self):
        assets_model.set_entries(self.editor.node, self.entries())

    def hydrate(self):
        """Fill UI with values from node."""
        super(AssetsSection, self).hydrate()
        node = self.editor.node
        self.list_component.addItems(assets_model.get_entries(node))
