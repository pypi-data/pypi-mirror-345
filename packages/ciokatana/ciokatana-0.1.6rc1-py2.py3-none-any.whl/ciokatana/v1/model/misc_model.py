import re
import os
from ciokatana.v1 import const as k

DEFAULT_NOTIFICATIONS = "artist@example.com, producer@!example.com"
NOTIFICATIONS_PARAM = "notifications"
USE_NOTIFICATIONS_PARAM = "useNotifications"
LOCATION_PARAM = "location"
USE_DAEMON_PARAM = "useUploadDaemon"
AUTOSAVE_SCENE_PARAM = "autosave"
CLEANUP_SCENE_PARAM = "cleanupAutosave"

# DEVELOPER
DEV_MODE_PARAM = "devMode"
USE_FIXTURES_PARAM = "useFixtures"
USE_MOCK_SUBMISSION_PARAM = "useMock"
MOCK_SUBMISSION_FILE_PARAM = "mockFile"
GENERATE_MOCK_SUBMISSION_PARAM = "generateMock"
MOCK_SUBMISSION_PROGRESS_FREQUENCY_PARAM = "mockProgressFrequency"

USE_MOCK_DEFAULT_VALUE = 0

DEFAULT_MOCK_FILE = os.path.join( os.path.expanduser(os.path.join("~", "mock_submission.json")))

def create(node):
    params = node.getParameters()
    params.createChildNumber(USE_NOTIFICATIONS_PARAM, 0)
    params.createChildString(NOTIFICATIONS_PARAM, DEFAULT_NOTIFICATIONS)
    params.createChildString(LOCATION_PARAM, "")

    # To be removed
    params.createChildNumber(USE_DAEMON_PARAM, 0)
    params.createChildNumber(USE_FIXTURES_PARAM, 1) # goes in developer section
    
    params.createChildNumber(USE_MOCK_SUBMISSION_PARAM, USE_MOCK_DEFAULT_VALUE)
    params.createChildNumber(GENERATE_MOCK_SUBMISSION_PARAM, 0)
    params.createChildString(MOCK_SUBMISSION_FILE_PARAM, DEFAULT_MOCK_FILE )
    params.createChildNumber(MOCK_SUBMISSION_PROGRESS_FREQUENCY_PARAM, 0.05)


def get_mock_config(node):
    """Get the whole mock config as a dict."""
    if not k.ENABLE_MOCKS:
        return {
            "use_mock_submission":0,
            "generate_mock_submission": 0,
            "mock_submission_file":"",
            "mock_progress_frequency":0
        }

    return {
        "use_mock_submission": node.getParameter(USE_MOCK_SUBMISSION_PARAM).getValue(0),
        "generate_mock_submission": node.getParameter(
            GENERATE_MOCK_SUBMISSION_PARAM
        ).getValue(0),
        "mock_submission_file": node.getParameter(MOCK_SUBMISSION_FILE_PARAM).getValue(
            0
        ),
        "mock_progress_frequency": node.getParameter(
            MOCK_SUBMISSION_PROGRESS_FREQUENCY_PARAM
        ).getValue(0),
    }


def set_mock_mode(node, value):
    """Set the 2 mock mode parameters based on the UI dropdown menu."""
    if value == 2:
        node.getParameter(USE_MOCK_SUBMISSION_PARAM).setValue(0, 0)
        node.getParameter(GENERATE_MOCK_SUBMISSION_PARAM).setValue(1, 0)
    elif value == 1:
        node.getParameter(USE_MOCK_SUBMISSION_PARAM).setValue(1, 0)
        node.getParameter(GENERATE_MOCK_SUBMISSION_PARAM).setValue(0, 0)
    else:
        node.getParameter(USE_MOCK_SUBMISSION_PARAM).setValue(0, 0)
        node.getParameter(GENERATE_MOCK_SUBMISSION_PARAM).setValue(0, 0)


def get_mock_mode(node):
    """Get the mock mode as an integer.
    
    We can hydrate the UI dropdown menu with this value.
    """
    if not k.ENABLE_MOCKS:
        return 0
    use_mock = node.getParameter(USE_MOCK_SUBMISSION_PARAM).getValue(0)
    gen_mock = node.getParameter(GENERATE_MOCK_SUBMISSION_PARAM).getValue(0)
    if use_mock:
        return 1
    elif gen_mock:
        return 2
    else:
        return 0


def resolve(node):
    """Resolve the notifications and location section of the payload."""
    result = {}
    notifications = node.getParameter(NOTIFICATIONS_PARAM).getValue(0)
    if notifications:
        if notifications:
            result["notify"] = {
                "emails": [a for a in re.split(r"[, ]+", notifications) if a]
            }

    location = node.getParameter(LOCATION_PARAM).getValue(0)
    if location:
        result["location"] = location

    result["local_upload"] = not node.getParameter(USE_DAEMON_PARAM).getValue(0)

    return result
