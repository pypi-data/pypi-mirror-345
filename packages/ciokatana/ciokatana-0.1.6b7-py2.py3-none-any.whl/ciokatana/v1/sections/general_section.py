from PyQt5 import QtGui
from ciocore import data as coredata
from ciokatana.v1.sections.collapsible_section import CollapsibleSection
from ciokatana.v1.components.combo_box_grp import ComboBoxGrp
from ciokatana.v1 import const as k
from ciokatana.v1.model import (
    project_model,
)
from ciokatana.v1.model.jobs_model import TITLE_PARAM



import UI4
import UI4.FormMaster.PythonValuePolicy


class GeneralSection(CollapsibleSection):
    """Section containing the most used settings

    project, etc.
    """

    ORDER = 10

    def __init__(self, editor):
        super(GeneralSection, self).__init__(editor, "General")

        factory = UI4.FormMaster.ParameterWidgetFactory
        group_policy_data = {"__childOrder": [TITLE_PARAM]}

        group_policy = UI4.FormMaster.PythonValuePolicy.PythonValuePolicy(
            "hiddenGroup", group_policy_data
        )
        group_policy.getWidgetHints()["hideTitle"] = True

        # Adds the title
        title_policy = UI4.FormMaster.CreateParameterPolicy(
            None, self.editor.node.getParameter(TITLE_PARAM)
        )
        title_policy.getWidgetHints().update({"help": k.TITLE_TIP})
        group_policy.addChildPolicy(title_policy)

        self.title_group_widget = factory.buildWidget(self, group_policy)

        self.content_layout.addWidget(self.title_group_widget)

        self.project_component = ComboBoxGrp(label="conductorProject", tooltip=k.PROJECT_TIP)

        self.content_layout.addWidget(self.project_component)

        self.rehydrate_qtmodel()

        self.configure_signals()

    def configure_signals(self): 
        self.project_component.combobox.currentTextChanged.connect(
            self.on_project_change
        )

    def rehydrate_qtmodel(self):
        """Rehydrate the combo box model.
        
        Tries to remember the existing value, and if it's still valid then use it. 
        """
        node = self.editor.node
        project = project_model.get_value(node)
        qtmodel = self.projects_qtmodel()
        self.project_component.set_model(qtmodel)
        project_model.set_value(node,project)


    def on_project_change(self, value):
        project_model.set_value(self.editor.node, value)

    def hydrate(self):
        """Fill UI with values from node."""
        node = self.editor.node
        super(GeneralSection, self).hydrate()
        project = project_model.get_value(node)
        self.project_component.set_by_text(project)

    @staticmethod
    def projects_qtmodel():
        """Provide the QT model for the projects compbobox options."""
        projects = coredata.data()["projects"] if coredata.valid() else []
        model = QtGui.QStandardItemModel()
        if not projects:
            projects = [k.NOT_CONNECTED]
        for project in projects:
            model.appendRow(QtGui.QStandardItem(project))
        return model
