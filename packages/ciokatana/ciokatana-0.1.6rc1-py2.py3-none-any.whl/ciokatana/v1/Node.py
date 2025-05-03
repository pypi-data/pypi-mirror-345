import logging
import traceback
from Katana import NodegraphAPI
from ciocore import loggeria, config
from ciocore import data as coredata
from ciocore import conductor_submit
from ciokatana.v1.model import (
    collapsible_panel_model,
    hardware_model,
    jobs_model,
    misc_model,
    project_model,
    software_model,
    environment_model,
    metadata_model,
    assets_model,
)

from ciokatana.v1 import const as k
from ciokatana.v1 import utils


# Setup logging
loggeria.setup_conductor_logging(
    logger_level=loggeria.LEVEL_MAP.get(config.get()["log_level"])
)
logger = logging.getLogger(__name__)

PAYLOAD_KEY_ORDER = [
    "job_title",
    "project",
    "output_path",
    "instance_type",
    "preemptible",
    "autoretry_policy",
    "scout_frames",
    "local_upload",
    "software_package_ids",
    "environment",
    "metadata",
    "tasks_data",
    "upload_paths",
]


class ConductorRenderNode(NodegraphAPI.SuperTool):
    """The node class that manages model attributes.

    There's no UI code in the node class or any models that its composed of. The
    node should be able to run in batch mode.
    """

    @classmethod
    def singleton_factory(cls):
        coredata.init(product="katana")
        coredata.data()

        rootNode = NodegraphAPI.GetRootNode()
        existing = NodegraphAPI.GetAllNodesByType(
            k.CONDUCTOR_RENDER_NODE_TYPE, includeDeleted=False, sortByName=True
        )
        if existing:
            conductor_node = existing[-1]
            for node in existing[:-1]:
                node.delete()
        else:
            conductor_node = NodegraphAPI.CreateNode(
                k.CONDUCTOR_RENDER_NODE_TYPE, rootNode
            )

        conductor_node.setName(k.CONDUCTOR_RENDER_NODE_NAME)

        return conductor_node

    def __init__(self):
        self.hideNodegraphGroupControls()
        self.addOutputPort("output")
        self.addInputPort("input")

        project_model.create(self)
        hardware_model.create(self)
        jobs_model.create(self)
        software_model.create(self)
        environment_model.create(self)
        metadata_model.create(self)
        assets_model.create(self)
        misc_model.create(self)
        collapsible_panel_model.create(self)

    @classmethod
    def connect(cls, force=False):
        """Establish communication with Conductor.

        coredata is a singleton that is used to store instance types, projects,
        and packages. If `force` is false, and coredata is already initialized,
        then no new data is fetched from Conductor. If `force` is true, then all
        data is fetched afresh.

        This method is called by the UI to initialize comboboxes and more. If
        user wants to submit in batch mode, they can call this method, since the
        UI won't do it for them.

        On submission, coredata is primarily needed to resolve the software
        environment and package ids. It's also useful for validating other
        values stored on the node. For example, if the user has an instance-type
        stored from a previous session and it no longer exists in coredata, then
        the submission will fail. He can instead check the values against
        coredata.data()["instance_types"] to make sure they exist.
        """

        with utils.wait_cursor():
            coredata.init(product="katana")
            coredata.data(force=force)

    @classmethod
    def resolve_common_payload(cls, node):
        """Construct the common payload for the node."""
        payload = {}
        payload.update(project_model.resolve(node))
        payload.update(hardware_model.resolve(node))
        payload.update(software_model.resolve(node))
        payload.update(environment_model.resolve(node))
        payload.update(metadata_model.resolve(node))
        payload.update(misc_model.resolve(node))
        payload.update(assets_model.resolve(node))
        return payload

    @classmethod
    def submit(cls, node):
        # The current file is assumed to not be dirty.
        responses = []
        for submission in cls.get_submissions(node):
            title = submission["job_title"]
            try:
                remote_job = conductor_submit.Submit(submission)
                response, response_code = remote_job.main()
            except BaseException as ex:
                msg = traceback.format_exc()
                response, response_code = msg, 500
            responses.append((response, response_code))

    @classmethod
    def get_submissions(cls, node):
        """Generate submission to the UI.

        1. Get the common stuff
        2. Merge in the per-node stuff and yield
        """
        common_payload = cls.resolve_common_payload(node)

        for render_node_payload in jobs_model.resolve(node):
            payload = common_payload.copy()
            payload.update(render_node_payload)

            output_path = payload["output_path"]
            upload_paths = payload["upload_paths"]
            payload["upload_paths"] = [
                path for path in upload_paths if not path.startswith(output_path)
            ]
            ordered_payload = {
                key: payload[key] for key in PAYLOAD_KEY_ORDER if key in payload
            }
            yield ordered_payload

    @classmethod
    def get_job_count(cls, node):
        """Get the number of submissions that will be generated."""
        return len(jobs_model.get_node_references(node))

    @classmethod
    def register_render_nodes(cls, conductor_node, render_nodes):
        """Set the render nodes to be used for the job."""
        jobs_model.set_node_references(conductor_node, render_nodes)
