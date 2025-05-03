from ciokatana.v1.sections.collapsible_section import CollapsibleSection
from ciokatana.v1.components.key_value_grp import KeyValueGrpList
from ciokatana.v1.model import environment_model


class EnvironmentSection(CollapsibleSection):
    """A sidget for editing the extra environment.

    It uses a KeyValueGrpList component which can configured with an extra
    boolean by provioding a checkbox_label.
    """

    ORDER = 60

    def __init__(self, editor):
        super(EnvironmentSection, self).__init__(editor, "Extra Environment")

        self.component = KeyValueGrpList(checkbox_label="Excl", key_label="Name")
        self.content_layout.addWidget(self.component)
        self.configure_signals()

    def configure_signals(self):
        self.component.edited.connect(self.on_edited)

    def on_edited(self):
        environment_model.set_entries(self.editor.node, self.component.entries())

    def hydrate(self):
        """Fill UI with values from node."""
        super(EnvironmentSection, self).hydrate()
        self.component.set_entries(environment_model.get_entries(self.editor.node))
