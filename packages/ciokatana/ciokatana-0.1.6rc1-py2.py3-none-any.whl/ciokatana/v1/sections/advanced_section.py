from ciokatana.v1.sections.collapsible_section import CollapsibleSection
from ciokatana.v1.components.combo_box_grp import ComboBoxGrp

from PyQt5 import QtGui


from ciokatana.v1.model import (
    misc_model,
)

from ciokatana.v1.model.jobs_model import POSIX_PROJECT_PARAM

from ciokatana.v1 import const as k

from ciokatana.v1.model.misc_model import (
    NOTIFICATIONS_PARAM,
    USE_NOTIFICATIONS_PARAM,
    LOCATION_PARAM,
    USE_FIXTURES_PARAM,
    USE_DAEMON_PARAM,
    MOCK_SUBMISSION_FILE_PARAM,
    MOCK_SUBMISSION_PROGRESS_FREQUENCY_PARAM,
)


import UI4
import UI4.FormMaster.PythonValuePolicy


class AdvancedSection(CollapsibleSection):
    ORDER = 100

    def __init__(self, editor):
        super(AdvancedSection, self).__init__(editor, "Advanced")

        factory = UI4.FormMaster.ParameterWidgetFactory
        group_policy_data = {
            "__childOrder": [
                USE_NOTIFICATIONS_PARAM,
                NOTIFICATIONS_PARAM,
                LOCATION_PARAM,
                USE_DAEMON_PARAM,
            ]
        }

        group_policy = UI4.FormMaster.PythonValuePolicy.PythonValuePolicy(
            "hiddenGroup", group_policy_data
        )
        group_policy.getWidgetHints()["hideTitle"] = True

        # use_daemon_policy = UI4.FormMaster.CreateParameterPolicy(
        #     None, self.editor.node.getParameter(USE_DAEMON_PARAM)
        # )
        # use_daemon_policy.getWidgetHints().update(
        #     {"widget": "checkBox", "constant": True}
        # )
        # group_policy.addChildPolicy(use_daemon_policy)

        # Adds the notifications
        use_notifications_policy = UI4.FormMaster.CreateParameterPolicy(
            None, self.editor.node.getParameter(USE_NOTIFICATIONS_PARAM)
        )
        use_notifications_policy.getWidgetHints().update(
            {"widget": "checkBox", "constant": True}
        )
        group_policy.addChildPolicy(use_notifications_policy)

        notifications_policy = UI4.FormMaster.CreateParameterPolicy(
            None, self.editor.node.getParameter(NOTIFICATIONS_PARAM)
        )
        # Hide the notifications field if the checkbox is not checked
        notifications_policy.getWidgetHints().update(
            {
                "conditionalVisOp": "equalTo",
                "conditionalVisPath": f"../{USE_NOTIFICATIONS_PARAM}",
                "conditionalVisValue": "1",
            }
        )

        group_policy.addChildPolicy(notifications_policy)

        # Adds the location
        location_policy = UI4.FormMaster.CreateParameterPolicy(
            None, self.editor.node.getParameter(LOCATION_PARAM)
        )
        group_policy.addChildPolicy(location_policy)

        self.main_widget = factory.buildWidget(self, group_policy)

        self.content_layout.addWidget(self.main_widget)

        if k.ENABLE_MOCKS:
            self.add_separator()

            self.mock_mode_component = ComboBoxGrp(label="mockMode")
            qtmodel = QtGui.QStandardItemModel()
            for option in ["Off", "Use Mock", "Generate Mock"]:
                qtmodel.appendRow(QtGui.QStandardItem(option))
            self.mock_mode_component.set_model(qtmodel)

            self.content_layout.addWidget(self.mock_mode_component)

            dev_group_policy_data = {
                "__childOrder": [
                    MOCK_SUBMISSION_FILE_PARAM,
                    MOCK_SUBMISSION_PROGRESS_FREQUENCY_PARAM,
                    USE_FIXTURES_PARAM,
                ]
            }

            dev_group_policy = UI4.FormMaster.PythonValuePolicy.PythonValuePolicy(
                "hidden", dev_group_policy_data
            )
            dev_group_policy.getWidgetHints()["hideTitle"] = True

            use_fixtures_policy = UI4.FormMaster.CreateParameterPolicy(
                None, self.editor.node.getParameter(USE_FIXTURES_PARAM)
            )
            use_fixtures_policy.getWidgetHints().update(
                {"widget": "checkBox", "constant": True}
            )
            dev_group_policy.addChildPolicy(use_fixtures_policy)

            posix_path_policy = UI4.FormMaster.CreateParameterPolicy(
                None, self.editor.node.getParameter(POSIX_PROJECT_PARAM)
            )
            dev_group_policy.addChildPolicy(posix_path_policy)

            mock_submission_file_policy = UI4.FormMaster.CreateParameterPolicy(
                None, self.editor.node.getParameter(MOCK_SUBMISSION_FILE_PARAM)
            )
            mock_submission_file_policy.getWidgetHints().update({"widget":"fileInput"})

            dev_group_policy.addChildPolicy(mock_submission_file_policy)

            mock_submission_progress_frequency_policy = (
                UI4.FormMaster.CreateParameterPolicy(
                    None,
                    self.editor.node.getParameter(
                        MOCK_SUBMISSION_PROGRESS_FREQUENCY_PARAM
                    ),
                )
            )
            mock_submission_progress_frequency_policy.getWidgetHints().update(
                {"constant": True, "min": "0.01", "strictLimits": True}
            )
            dev_group_policy.addChildPolicy(mock_submission_progress_frequency_policy)

            self.dev_widget = factory.buildWidget(self, dev_group_policy)

            self.content_layout.addWidget(self.dev_widget)

        self.configure_signals()

    def configure_signals(self):
        if k.ENABLE_MOCKS:
            self.mock_mode_component.combobox.currentTextChanged.connect(
                self.on_mock_mode_change
            )

    def hydrate(self):
        """Fill UI with values from node."""
        node = self.editor.node
        super(AdvancedSection, self).hydrate()
        if k.ENABLE_MOCKS:
            mock_mode = misc_model.get_mock_mode(node)
            self.mock_mode_component.combobox.setCurrentIndex(mock_mode)

    def on_mock_mode_change(self, _):
        value = self.mock_mode_component.combobox.currentIndex()
        misc_model.set_mock_mode(self.editor.node, value)
