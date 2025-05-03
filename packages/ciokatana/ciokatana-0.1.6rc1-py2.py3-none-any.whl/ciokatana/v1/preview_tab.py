from PyQt5 import  QtGui
from PyQt5.QtWidgets import QTextEdit
import UI4
import json
from ciokatana.v1.components.buttoned_scroll_panel import ButtonedScrollPanel
from ciokatana.v1.Node import ConductorRenderNode

class PreviewTab(ButtonedScrollPanel):
    def __init__(self, editor):
        super(PreviewTab, self).__init__(editor, buttons=[
            ("export", "Export Script (PRO)"), 
            ("next", "See Next Job"),
            ("validate", "Validate && Submit")
        ])
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.layout.addWidget(self.text_area)
        self.generator = None
        # self.buttons["export"].setEnabled(False)

        self.configure_signals()

    def configure_signals(self):
        """Connect signals to slots."""
        self.buttons["validate"].clicked.connect(self.on_validate_button)
        self.buttons["export"].clicked.connect(self.on_export_button)
        self.buttons["next"].clicked.connect(self.on_next_button)

    def show_next_job(self, reset=False):
        if reset or not self.generator:
            self.generator = ConductorRenderNode.get_submissions(self.editor.node)
        job = next(self.generator, None)
        if job == None:
            #reset the generator
            self.generator = ConductorRenderNode.get_submissions(self.editor.node)
            job = next(self.generator, None)
        self.text_area.setText(json.dumps(job, indent=3))
        
    def on_validate_button(self):
        """Initiate the submission with validations."""
        # validation runs before saving or changing anything
        self.editor.show_validation_tab()
        self.editor.validation_tab.hydrate()

    def on_export_button(self):
        UI4.Widgets.MessageBox.Warning(
            "Export Script", "This is a PRO feature. Please sign up for a Conductor Enterprise subscription in order export executable submission scripts."
        )
        return
    
    def on_next_button(self):
        self.show_next_job()