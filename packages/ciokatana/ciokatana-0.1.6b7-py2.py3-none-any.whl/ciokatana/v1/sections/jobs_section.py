from ciokatana.v1.sections.collapsible_section import CollapsibleSection
from ciokatana.v1 import const as k
from ciokatana.v1.components.render_node_table import RenderNodeTable
from ciokatana.v1.model import jobs_model
from ciokatana.v1.model.jobs_model import (
    CHUNK_SIZE_PARAM,
    FRAMES_PARAM,
    SCOUT_FRAMES_PARAM,
    TASK_TEMPLATE_PARAM
)


import UI4
import UI4.FormMaster.PythonValuePolicy

class JobsSection(CollapsibleSection):
    """Section containing frames, tasks, and multi-node info.
    
    There are 3 parameters in this section that are most likely to be edited by
    the user:
    
    * Chunk size - how many frames to render per task 
    * Frame spec - the frame rangeto render 
    * Scout spec - the frames to run immediately.
    
    There's also the task template parameter, which is an expression and not
    designed for regular editing.
    
    In addition, this section contains a table of render nodes and their
    settings for the above parameters. If the user has overridden the settings
    on a render node, the table will show the overridden values.
    
    The table is not editable, but the user can click on the `Editor` button to
    show the node in an editor.
    
    When the user edits the conductor farm settings on a render node, or edit's
    its name, the table will reflect the overridden values.
    
    """

    ORDER = 20

    def __init__(self, editor):
        """Create widgets for the section."""
        super(JobsSection, self).__init__(editor, "Frames and Tasks")

        factory = UI4.FormMaster.ParameterWidgetFactory
        group_policy_data = {
            "__childOrder": [
                CHUNK_SIZE_PARAM,
                FRAMES_PARAM,
                SCOUT_FRAMES_PARAM,
                TASK_TEMPLATE_PARAM,
            ]
        }

        group_policy = UI4.FormMaster.PythonValuePolicy.PythonValuePolicy(
            "hiddenGroup", group_policy_data
        )
        group_policy.getWidgetHints()["hideTitle"] = True

        # Adds the chunk size
        chunk_size_policy = UI4.FormMaster.CreateParameterPolicy(
            None, self.editor.node.getParameter(CHUNK_SIZE_PARAM)
        )
        chunk_size_policy.getWidgetHints().update(
            {"constant": True, "int": True, "min": "1", "strictLimits": True}
        )
        group_policy.addChildPolicy(chunk_size_policy)

        # Adds the frame spec
        frames_policy = UI4.FormMaster.CreateParameterPolicy(
            None, self.editor.node.getParameter(FRAMES_PARAM)
        )
        group_policy.addChildPolicy(frames_policy)

        # Adds the scout frames
        scout_frames_policy = UI4.FormMaster.CreateParameterPolicy(
            None, self.editor.node.getParameter(SCOUT_FRAMES_PARAM)
        )
        group_policy.addChildPolicy(scout_frames_policy)

        # Adds the task template
        task_template_policy = UI4.FormMaster.CreateParameterPolicy(
            None, self.editor.node.getParameter(TASK_TEMPLATE_PARAM)
        )
        group_policy.addChildPolicy(task_template_policy)

        self.widget = factory.buildWidget(self, group_policy)

        self.content_layout.addWidget(self.widget)

        # This is the PyQT table of render nodes
        self.jobs_component = RenderNodeTable()
        self.content_layout.addWidget(self.jobs_component)

    def hydrate(self):
        """Fill UI with values from the node."""
        super(JobsSection, self).hydrate()
        entries = list(jobs_model.resolve_overrides(self.editor.node))
        self.jobs_component.set_entries(entries)
        
    def render_node_changed(self, render_node):
        """Update the table UI when a render node is changed.
        """
        render_node_data = jobs_model.resolve_overrides(self.editor.node)
        indexed_data = next(
            (p for p in enumerate(render_node_data) if p[1]["render_node"] == render_node),
            None,
        )
        if not indexed_data:
            return

        index, data = indexed_data
        self.jobs_component.hydrate_entry(index, data)
        
    def conductor_node_changed(self, node):
        """Update the table UI when the ConductorRender node is changed.
        """
        entries = list(jobs_model.resolve_overrides(self.editor.node))
        self.jobs_component.set_entries(entries)
