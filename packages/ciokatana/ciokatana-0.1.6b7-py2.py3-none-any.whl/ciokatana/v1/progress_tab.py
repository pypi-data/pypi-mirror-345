from ciokatana.v1.components.buttoned_scroll_panel import ButtonedScrollPanel
from ciokatana.v1.Node import ConductorRenderNode
from ciokatana.v1.progress.md5_progress_widget import MD5ProgressWidget
from ciokatana.v1.progress.upload_progress_widget import UploadProgressWidget
from ciokatana.v1.progress.jobs_progress_widget import JobsProgressWidget

from ciokatana.v1.progress.file_status_panel import FileStatusPanel
from ciokatana.v1.progress.submission_worker import SubmissionWorkerBase
from ciokatana.v1.model import misc_model


import os
import json
import logging

from PyQt5.QtCore import QThreadPool


logger = logging.getLogger(__name__)


class ProgressTab(ButtonedScrollPanel):
    """The progress tab.

    Shows the progress of the submissions with 4 elements:

    1. Jobs progress: Shows the progress of the entire batch of jobs.
    2. MD5 progress: Shows the progress of the MD5 generation for the current job.
    3. Upload progress: Shows the progress of the upload for the current job.
    4. File status: Shows detailed progress for each file.

    """

    def __init__(self, editor):
        super(ProgressTab, self).__init__(
            editor, buttons=[("raise", "Raise an error"), ("cancel", "Cancel")]
        )

        self.progress_list = []
        self.responses = []

        self.create_mock = None
        self.mock_file = None
        self.mock_file_handle = None
        self.pin = None
        self.use_mock = None
        self.mock_frequency = None

        self.jobs_widget = JobsProgressWidget()
        self.md5_widget = MD5ProgressWidget()
        self.upload_widget = UploadProgressWidget()
        self.file_status_panel = FileStatusPanel()

        self.layout.addWidget(self.jobs_widget)
        self.layout.addWidget(self.md5_widget)
        self.layout.addWidget(self.upload_widget)
        self.layout.addWidget(self.file_status_panel)

        self.buttons["cancel"].clicked.connect(self.on_cancel_button)
        self.buttons["raise"].clicked.connect(self.on_raise_button)
        self.buttons["raise"].setVisible(False)

    def _set_mock_members(self):
        """Sets the mock settings.

        Mocks progress by reading from a file. This is useful for testing, and
        for demonstrating.

        """
        mock_config = misc_model.get_mock_config(self.editor.node)

        self.create_mock = mock_config["generate_mock_submission"]
        self.mock_file = mock_config["mock_submission_file"]
        self.use_mock = mock_config["use_mock_submission"]
        self.mock_frequency = mock_config["mock_progress_frequency"]

    def submit(self):
        """Submits the jobs.

        Send the submission generator to the worker, along with some info about use of mocks.
        """

        self.jobs_widget.reset()
        self.md5_widget.reset()
        self.upload_widget.reset()
        self.file_status_panel.reset()

        self._set_mock_members()

        # This is a fake raise and is only recognized while using the mock submission worker.
        self.buttons["raise"].setVisible(int(self.use_mock))

        self.responses = []

        submissions = ConductorRenderNode.get_submissions(self.editor.node)
        job_count = ConductorRenderNode.get_job_count(self.editor.node)

        if not submissions:
            logger.info("No submissions found")
            return

        self.threadpool = QThreadPool()

        self.worker = SubmissionWorkerBase.create(
            submissions,
            job_count,
            self.use_mock,
            self.mock_file,
            self.mock_frequency,
        )
        self.worker.signals.on_start.connect(self.jobs_widget.reset)
        self.worker.signals.on_job_start.connect(self.md5_widget.reset)
        self.worker.signals.on_job_start.connect(self.upload_widget.reset)
        self.worker.signals.on_progress.connect(self.md5_widget.set_progress)
        self.worker.signals.on_progress.connect(self.upload_widget.set_progress)
        self.worker.signals.on_progress.connect(self.jobs_widget.set_progress)
        self.worker.signals.on_progress.connect(self.file_status_panel.set_progress)
        self.worker.signals.on_response.connect(self.handle_response)
        self.worker.signals.on_done.connect(self.handle_done)
        self.worker.signals.on_error.connect(self.handle_error)

        if self.create_mock:
            # collect event packets so they can be saved to a file.
            self.worker.signals.on_start.connect(self.write_mock_start)
            self.worker.signals.on_job_start.connect(self.write_mock_job_start)
            self.worker.signals.on_progress.connect(self.write_mock_progress)
            self.worker.signals.on_response.connect(self.write_mock_response)
            self.worker.signals.on_error.connect(self.write_mock_error)
            self.worker.signals.on_done.connect(self.write_mock_done)

        self.threadpool.start(self.worker)

    def handle_response(self, response):
        """Handle the job submitted response.

        We add in some extra information to help identify the job within the batch.
        """
        self.responses.append(response)

    def handle_error(self, error):
        """Make an error string from the exception and push it onto the responses."""
        self.responses.append(error)

    def on_cancel_button(self):
        if self.worker:
            self.worker.cancel()

    def on_raise_button(self):
        if self.worker:
            self.worker.raise_exception()

    def handle_done(self):
        self.editor.show_response_tab()
        self.editor.response_tab.hydrate(self.responses)

    def write_mock_start(self, data):
        """Open JSON file for write.
        Write the start of the mock submission "[".
        """
        try:
            self.mock_file_handle = open(self.mock_file, "w")
            self.mock_file_handle.write("[\n")
            self.mock_file_handle.write(
                json.dumps({"event": "start", "data": data}, indent=4)
            )
        except Exception as e:
            self.mock_file_handle.close()

    def write_mock_job_start(self, job):
        """Write the start of a job to the mock file."""
        # if not self.pin == "start":
        self.mock_file_handle.write(",\n")
        self.mock_file_handle.write(
            json.dumps({"event": "job_start", "data": job}, indent=4)
        )
        self.pin = ""

    def write_mock_progress(self, progress):
        """write a progress event to the mock file"""
        self.mock_file_handle.write(",\n")
        self.mock_file_handle.write(
            json.dumps({"event": "progress", "data": progress}, indent=4)
        )

    def write_mock_response(self, response):
        self.mock_file_handle.write(",\n")
        self.mock_file_handle.write(
            json.dumps(
                {
                    "event": "response",
                    "data": response,
                },
                indent=4,
            )
        )

    def write_mock_error(self, error):
        self.mock_file_handle.write(",\n")
        self.mock_file_handle.write(
            json.dumps({"event": "error", "data": error}, indent=4)
        )

    def write_mock_done(self):
        """close the submission JSON and close the file"""
        self.mock_file_handle.write(",\n")
        self.mock_file_handle.write(json.dumps({"event": "done"}, indent=4))
        self.mock_file_handle.write("]\n")
        self.mock_file_handle.close()
