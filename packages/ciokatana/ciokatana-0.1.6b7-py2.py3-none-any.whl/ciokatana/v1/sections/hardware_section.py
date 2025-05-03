from PyQt5 import QtGui
from ciocore import data as coredata

from ciokatana.v1.sections.collapsible_section import CollapsibleSection
from ciokatana.v1.components.combo_box_grp import DualComboBoxGrp
from ciokatana.v1.model import hardware_model
from ciokatana.v1 import utils

from ciokatana.v1.model.hardware_model import (
    INSTANCE_TYPE_PARAM,
    PREEMPTIBLE_PARAM,
    RETRIES_PARAM,
)


import UI4
import UI4.FormMaster.PythonValuePolicy

class HardwareSection(CollapsibleSection):
    ORDER = 15

    def __init__(self, editor):
        super(HardwareSection, self).__init__(editor, "Hardware")

        self.instance_type_component = DualComboBoxGrp(
            direction="row", label=INSTANCE_TYPE_PARAM, width1=70
        )
        self.content_layout.addWidget(self.instance_type_component)

        factory = UI4.FormMaster.ParameterWidgetFactory
        group_policy_data = {"__childOrder": [PREEMPTIBLE_PARAM, RETRIES_PARAM]}
        group_policy = UI4.FormMaster.PythonValuePolicy.PythonValuePolicy(
            "hiddenGroup", group_policy_data
        )
        group_policy.getWidgetHints()["hideTitle"] = True

        preemptible_policy = UI4.FormMaster.CreateParameterPolicy(
            None, self.editor.node.getParameter(PREEMPTIBLE_PARAM)
        )
        preemptible_policy.getWidgetHints().update(
            {"widget": "checkBox", "constant": True}
        )
        group_policy.addChildPolicy(preemptible_policy)

        retries_policy = UI4.FormMaster.CreateParameterPolicy(
            None, self.editor.node.getParameter(RETRIES_PARAM)
        )
        retries_policy.getWidgetHints().update(
            {
                "conditionalVisOp": "equalTo",
                "conditionalVisPath": f"../{PREEMPTIBLE_PARAM}",
                "conditionalVisValue": "1",
                "int": True,
                "min": "0",
                "max": "5",
                "constant": True,
                "strictLimits": True,
            }
        )

        group_policy.addChildPolicy(retries_policy)

        self.widget = factory.buildWidget(self, group_policy)

        self.content_layout.addWidget(self.widget)

        self.rehydrate_qtmodel()

        self.configure_signals()

    def configure_signals(self):
        self.instance_type_component.combobox_content.currentTextChanged.connect(
            self.on_instance_type_change
        )
        
    def rehydrate_qtmodel(self):
        """Rehydrate the combo box model.
        
        Tries to remember the existing value, and if it's still valid then use it. 
        """
        node = self.editor.node
        instance_type_name = hardware_model.get_value(node)
        qtmodel = self.get_instance_types_qtmodel()
        self.instance_type_component.set_model(qtmodel)
        hardware_model.set_value(node, instance_type_name)


    def on_instance_type_change(self, value):
        """
        Persist the instance type selection to the node.

        The value we persist is the name of the instance type. In the example object returned from
        DualComboBoxGrp.get_current_data() below, the name is the second
        item in the content list. It uniquely identifies the instance type.

        {
            "category": "GPU",
            "content": [
                "4 core, 15GB Mem (1 T4 Tensor GPU with 16GB Mem)",
                "n1-standard-4-t4-1"
            ]
        }

        The full path can be passed to DualComboBoxGrp.set_by_text() to select
        the instance type when rehydrating the widget.

        """
        data = self.instance_type_component.get_current_data()
        hardware_model.set_value(self.editor.node, data["content"][1])

    def hydrate(self):
        """Fill UI with values from node."""
        node = self.editor.node

        super(HardwareSection, self).hydrate()

        self.instance_type_component.set_by_text(
            hardware_model.get_value(node), column=1
        )

    @staticmethod
    def get_instance_types_qtmodel():
        hardware = utils.unconnected_hardware()
        if (
            coredata.valid()
            and coredata.data().get("instance_types")
            and coredata.data().get("instance_types").categories
        ):
            hardware = coredata.data().get("instance_types")

        category_labels = [category["label"] for category in hardware.categories]

        model = QtGui.QStandardItemModel()
        for category_label in category_labels:
            item = QtGui.QStandardItem(category_label)
            category = hardware.find_category(category_label)
            if not category:
                continue
            for entry in category["content"]:
                item.appendRow(
                    (
                        QtGui.QStandardItem(entry["description"]),
                        QtGui.QStandardItem(entry["name"]),
                    )
                )
            model.appendRow(item)
        return model
