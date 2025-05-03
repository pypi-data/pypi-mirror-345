
# Import for introspection
from ciokatana.v1.sections.general_section import GeneralSection
from ciokatana.v1.sections.hardware_section import HardwareSection
from ciokatana.v1.sections.software_section import SoftwareSection
from ciokatana.v1.sections.environment_section import EnvironmentSection
from ciokatana.v1.sections.jobs_section import JobsSection
from ciokatana.v1.sections.metadata_section import MetadataSection
from ciokatana.v1.sections.assets_section import AssetsSection
from ciokatana.v1.sections.advanced_section import AdvancedSection
from ciokatana.v1.sections.collapsible_section import CollapsibleSection

from ciokatana.v1.components.buttoned_scroll_panel import ButtonedScrollPanel
from ciokatana.v1.Node import ConductorRenderNode

class MainTab(ButtonedScrollPanel):
    """
    Build the tab that contains the configuration sections.

    """

    def __init__(self, editor):
        super(MainTab, self).__init__(
            editor,
            buttons=[
                ("reconnect", "Reconnect"),
                ("validate", "Validate && Submit"),
            ],
        )

        self.sections = self._create_sections(self.layout)
        
        self.layout.addStretch()
        self.configure_signals()

    def _create_sections(self, layout):
        """Create the sections that will be displayed in the tab.
        
        We create find classes that inherit from CollapsibleSection and sort
        them by their ORDER attribute. We then create an instance of each class
        and add it to the layout.
        """
        self._section_classes = sorted(
            CollapsibleSection.__subclasses__(), key=lambda x: x.ORDER
        )
        sections = [cls(self.editor) for cls in self._section_classes]
        
        for section in sections:
            layout.addWidget(section)
        
        return sections

    def hydrate(self):
        """Fill UI with values from node."""
        for section in self.sections:
            section.hydrate()

    def configure_signals(self):
        """Connect signals to slots."""
        self.buttons["validate"].clicked.connect(self.on_validate_button)
        self.buttons["reconnect"].clicked.connect(self.on_reconnect_button)

    def on_validate_button(self):
        
        """Initiate the submission wit validations."""
        # validation runs before saving or changing anything
        self.editor.show_validation_tab()
        self.editor.validation_tab.hydrate()

    def on_reconnect_button(self):
        """Reconnect to Conductor.
        
        Read the endpoints, repopulate the menus, and rehydrate the UI.
        """
        ConductorRenderNode.connect(force=True)
        self.section("GeneralSection").rehydrate_qtmodel()
        self.section("HardwareSection").rehydrate_qtmodel()
        self.section("SoftwareSection").rehydrate_qtmodel()
        self.hydrate()

    def section(self, classname):
        """
        Convenience to find sections by name.
        
        Example: section("EnvironmentSection").some_method()
        
        NOTE: This is likely not needed. UI components should be able to get
        what they need directly from model classes.
        """
        return next(s for s in self.sections if s.__class__.__name__ == classname)
