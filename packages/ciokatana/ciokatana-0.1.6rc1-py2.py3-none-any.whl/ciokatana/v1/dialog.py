import logging
from ciokatana.v1 import const as k
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
)


from ciokatana.v1.Panel import ConductorRenderPanel

from ciokatana.v1.model.jobs_model import (
    CHUNK_SIZE_PARAM,
    FRAMES_PARAM,
    SCOUT_FRAMES_PARAM,
    FARM_SETTING_OVERRIDES_PARAM,
    FARM_SETTING_FRAMESPEC_PARAM,
    FARM_SETTING_SCOUTSPEC_PARAM,
    FARM_SETTING_CHUNKSIZE_PARAM,
)

from Katana import Utils
import UI4
import UI4.FormMaster.PythonValuePolicy

logger = logging.getLogger(__name__)


class ConductorRenderDialog(QDialog):
    """
    Encapsulate the ConductorRenderPanel in a dialog.
    """

    # Consider moving these events handlers to the panel
    def closeEvent(self, event):
        if hasattr(self, "render_node_rename_callback"):
            if Utils.EventModule.IsHandlerRegistered(
                self.render_node_rename_callback, "node_setName"
            ):
                Utils.EventModule.UnregisterEventHandler(
                    self.render_node_rename_callback, "node_setName"
                )
        if hasattr(self, "frame_settings_callback"):
            if Utils.EventModule.IsHandlerRegistered(
                self.frame_settings_callback, "parameter_finalizeValue"
            ):
                Utils.EventModule.UnregisterEventHandler(
                    self.frame_settings_callback, "parameter_finalizeValue"
                )

    def __init__(self, node):
        QDialog.__init__(self, UI4.App.MainWindow.GetMainWindow())

        self.setWindowTitle("Conductor Render")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.panel = ConductorRenderPanel(self, node)
        self.layout.addWidget(self.panel)
        self.setup_event_handlers()

    def setup_event_handlers(self):
        """
        Setup event handlers.
        """

        # Consider moving these events handlers to the panel

        Utils.EventModule.RegisterEventHandler(
            self.render_node_rename_callback, "node_setName"
        )
        Utils.EventModule.RegisterEventHandler(
            self.frame_settings_callback, "parameter_finalizeValue"
        )

    def render_node_rename_callback(self, eventType, eventID, **kwargs):
        """Update the table UI when a render node is renamed."""
        node = kwargs["node"]
        if not node.getType() == "Render":
            return
        self.panel.configuration_tab.section("JobsSection").render_node_changed(node)

    def frame_settings_callback(self, eventType, eventID, **kwargs):
        """Update the table UI frame values."""
        node = kwargs["node"]
        param = kwargs["param"]
        node_type = node.getType()
        if not node_type in ["Render", k.CONDUCTOR_RENDER_NODE_TYPE]:
            return
        if node_type == "Render":
            if not param.getName() in [
                FARM_SETTING_OVERRIDES_PARAM.split(".")[-1],
                FARM_SETTING_FRAMESPEC_PARAM.split(".")[-1],
                FARM_SETTING_SCOUTSPEC_PARAM.split(".")[-1],
                FARM_SETTING_CHUNKSIZE_PARAM.split(".")[-1],
            ]:
                return
            self.panel.configuration_tab.section("JobsSection").render_node_changed(node)

        if node_type == k.CONDUCTOR_RENDER_NODE_TYPE:
            if not param.getName() in [
                CHUNK_SIZE_PARAM,
                FRAMES_PARAM,
                SCOUT_FRAMES_PARAM,
            ]:
                return
            self.panel.configuration_tab.section("JobsSection").conductor_node_changed(node)
