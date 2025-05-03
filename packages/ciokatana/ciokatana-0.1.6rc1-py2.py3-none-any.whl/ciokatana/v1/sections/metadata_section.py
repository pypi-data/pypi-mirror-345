from ciokatana.v1.sections.collapsible_section import CollapsibleSection
from ciokatana.v1.components.key_value_grp import KeyValueGrpList
from ciokatana.v1.model import metadata_model

class MetadataSection(CollapsibleSection):
    ORDER = 70

    def __init__(self, editor):
        super(MetadataSection, self).__init__(editor, "Metadata")

        self.component = KeyValueGrpList()
        self.content_layout.addWidget(self.component)
        self.configure_signals()

    def configure_signals(self):
        self.component.edited.connect(self.on_edited)

    def on_edited(self):
        metadata_model.set_entries(self.editor.node, self.component.entries())

    def hydrate(self):
        super(MetadataSection, self).hydrate()
        self.component.set_entries(metadata_model.get_entries(self.editor.node))

