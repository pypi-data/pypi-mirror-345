from ciokatana.v1.components.buttoned_scroll_panel import ButtonedScrollPanel
from ciokatana.v1.components.notice_grp import NoticeGrp
from ciokatana.v1 import validation
from ciokatana.v1 import utils
from ciokatana.v1 import render_file_dialog
from ciokatana.v1.model import misc_model
from Katana import (
    NodegraphAPI,
    KatanaFile,
)

SUMMARY_ERRORS = """Critical issues found. Please fix them before you submit."""
SUMMARY_WARNINGS = """Warnings found. Please review them before you submit.
You may continue, but please be aware that your job may not render as expected.""" 
SUMMARY_NOTICES = """No issues found. However, you may want to review the following information before you submit"""
SUMMARY_NONE = """No issues found. Press the Submit button to send your renders to Conductor."""

class ValidationTab(ButtonedScrollPanel):
    def __init__(self, editor):
        super(ValidationTab, self).__init__(
            editor, buttons=[("back", "Back"), ("submit", "Submit")]
        )
        self.configure_signals()

    def configure_signals(self):
        self.buttons["back"].clicked.connect(self.on_back)
        self.buttons["submit"].clicked.connect(self.on_submit)

    def hydrate(self):
        with utils.wait_cursor():
            errors, warnings, notices = validation.run(self.editor.node)
        self.clear()


        summary, severity = self._create_summary_notice(errors, warnings, notices)
        summary_widget = NoticeGrp(summary, severity)
        self.layout.addWidget(summary_widget)
        
        obj = {"error": errors, "warning": warnings, "info": notices}
        for severity in ["error", "warning", "info"]:
            for entry in obj[severity]:
                widget = NoticeGrp(entry, severity)

                self.layout.addWidget(widget)
        self.layout.addStretch()

        self.buttons["submit"].setEnabled(not errors)

    def _create_summary_notice(self, errors, warnings, notices):
        if not (errors or warnings or notices):
            return (SUMMARY_NONE, "info")
        if errors:
            return (SUMMARY_ERRORS, "error")
        if warnings:
            return (SUMMARY_WARNINGS, "warning")
        if notices:
            return (SUMMARY_NOTICES, "info")

    def on_submit(self):
        do_save = KatanaFile.IsFileDirty()

        use_mock = misc_model.get_mock_config(self.editor.node)["use_mock_submission"]

        if not use_mock:
            project_filename = NodegraphAPI.GetProjectFile()
            if do_save:
                result = render_file_dialog.show_dialog(project_filename)
                if result is not None:
                    KatanaFile.Save(result)
                else:
                    return

        self.editor.show_progress_tab()
        self.editor.progress_tab.submit()
