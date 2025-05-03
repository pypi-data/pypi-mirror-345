from PyQt5 import QtGui
from ciokatana.v1.sections.collapsible_section import CollapsibleSection
from ciokatana.v1.components.combo_box_grp import ComboBoxGrp, DualComboBoxGrp
from ciocore import data as coredata
from ciokatana.v1 import const as k
from ciokatana.v1.model import software_model
import logging

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


NO_RENDERER = {"name": "", "label": "Built-in (3Delight)"}


class SoftwareSection(CollapsibleSection):
    """Manage package selection.

    Use a dual combo box to select the host and renderer versions.
    """

    ORDER = 15

    def __init__(self, editor):
        """
        Combo box.

        """
        super(SoftwareSection, self).__init__(editor, "Software")

        self.component = DualComboBoxGrp(
            direction="column", label1="hostVersion", label2="rendererVersion"
        )

        self.content_layout.addWidget(self.component)


        self.rehydrate_qtmodel()

        self.component.combobox_content.currentTextChanged.connect(
            self.on_software_change
        )

    def rehydrate_qtmodel(self):
        """Rehydrate the combo box model.
        
        Tries to remember the existing value, and if it's still valid then use it. 
        """
        node = self.editor.node
        software_value  = software_model.get_value(node)
        qtmodel = self.get_software_qtmodel()
        self.component.set_model(qtmodel)
        software_model.set_value(node, software_value)

    def on_software_change(self, value):
        """
        Persist the software selection to the node.

        The value we persist is the full path to the renderer. It includes the
        Katana host version. In the example object returned from
        DualComboBoxGrp.get_current_data() below, the full path is the second
        item in the content list. It uniquely identifies the renderer.

        {
            "category": "high availability",
            "content": [
                "renderman-katana 22.3.1923604.0",
                "katana 3.2.6 linux|renderman-katana 22.3.1923604.0 linux"
            ]
        }

        The full path can be passed to DualComboBoxGrp.set_by_text() to select
        the renderer when rehydrating the widget.

        """
        data = self.component.get_current_data()
        software_model.set_value(self.editor.node, data["content"][1])

    def hydrate(self):
        """Fill UI with values from node."""
        node = self.editor.node
        super(SoftwareSection, self).hydrate()
        value = software_model.get_value(node)
        self.component.set_by_text(value, column=1)

    @staticmethod
    def get_software_qtmodel():
        """Build the QStandardItemModel to populate the software combo boxes."""

        model = QtGui.QStandardItemModel()

        software_data = coredata.valid() and coredata.data()["software"]
        if not software_data:
            host_names = [k.NOT_CONNECTED]
        else:
            host_names = software_data.supported_host_names()

        host_items = []

        for host_name in host_names:
            host_label = host_name.rpartition(" ")[0]
            host_item = QtGui.QStandardItem(host_label)
            host_items.append(host_item)
            renderers = software_data.supported_plugins(host_name) or []
            for renderer in renderers:
                for version in renderer["versions"]:
                    renderer_label = "{} {}".format(renderer["plugin"], version)
                    full_path = software_model.construct_full_path(
                        host_name, renderer_label
                    )

                    host_item.appendRow(
                        (
                            QtGui.QStandardItem(renderer_label),
                            QtGui.QStandardItem(full_path),
                        )
                    )
            full_path_no_renderer = "{}/{}".format(host_name, NO_RENDERER["name"])
            host_item.appendRow(
                (
                    QtGui.QStandardItem(NO_RENDERER["label"]),
                    QtGui.QStandardItem(full_path_no_renderer),
                )
            )
        for host_item in host_items:
            model.appendRow(host_item)
        return model
