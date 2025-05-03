# from PyQt5 import QtGui

from ciocore import data as coredata
from ciokatana.v1 import const as k
import logging

logger = logging.getLogger(__name__)


INITIAL_VALUE = k.NOT_CONNECTED  # host-version/plugin-version

SOFTWARE_PARAM = "software"

def create(node):
    """
    Create the parameter.

    The parameter value is the full path to the renderer. It includes the Katana
    host version. Both the host and renderer versions are qualified by platform.
    Example: katana 3.2.6 linux|renderman-katana 22.3.1923604.0 linux The
    renderer is optional, and the absence of a renderer implies the bundled
    3DLight will be used.
    
    The initial value is either the most recent host version or the string "Not
    Connected".
    """
    initial_value = _valid_value(k.NOT_CONNECTED)
    node.getParameters().createChildString(SOFTWARE_PARAM, initial_value)

def set_value(node, value):
    node.getParameter(SOFTWARE_PARAM).setValue(value, 0)

def get_value(node):
    value = node.getParameter(SOFTWARE_PARAM).getValue(0)
    valid_value = _valid_value(value)
    if valid_value != value:
        set_value(node, valid_value)
        return valid_value    
    return value

def set_value(node, value):
    valid_value = _valid_value(value)
    node.getParameter(SOFTWARE_PARAM).setValue(valid_value, 0)


def get_paths(node):
    """Getter to get valid paths from the software parameter value.
    
    Make sure it's valid.
    """
    stored_value = node.getParameter(SOFTWARE_PARAM).getValue(0)
    return _get_valid_paths(stored_value)



def _valid_value(value):
    all_paths = _get_valid_paths(value)
    return all_paths[-1]


def _get_valid_paths(value):
    """If connected, ensure the parameter is available.

    If it isn't, set to the most recent host version.
    
    Example:
    
    [
        host,
        host/plugin
    ]
    
    where both hjost and plugin are comprised of (name version platform)
    """
    all_paths = []
    parts = value.split("/")
    if len(parts) > 0:
        all_paths.append(parts[0])
        if len(parts) > 1 and parts[1]:
            all_paths.append(value)

    if not coredata.valid():
        # we don't know if the current value is valid, so just return the current value.
        return all_paths

    software_data = coredata.data()["software"]

    for i, path in enumerate(all_paths):
        package = software_data.find_by_path(path)
        if not package:
            host_names = software_data.supported_host_names()
            if i == 0:  # host path
                if not host_names:
                    return [INITIAL_VALUE]
                all_paths[0] = host_names[-1]
            else: 
                # There was a valid host, but invalid renderer. We'll remove
                # renderer and assume using built-in renderer.
                all_paths = [all_paths[0]]

    return all_paths


def resolve(node):
    """
    Return software package IDs.

    ['katana 4.0.5 linux', 'katana 4.0.5 linux/renderman-katana 1.2.3 linux']
    """ 
    result = []
    if coredata.valid():
        tree_data = coredata.data()["software"]
        for path in get_paths(node):
            package = tree_data.find_by_path(path)
            if package:
                result.append(package["package_id"])

    return {"software_package_ids": result}

def construct_full_path(host, renderer):
    """
    Construct the full path to the renderer.

    The full path is the host version and renderer version qualified by platform.
    Example:
        katana 3.2.6 linux|renderman-katana 22.3.1923604.0 linux

    """
    host_parts = host.split(" ")
    renderer_parts = renderer.split(" ")
    if len(host_parts) < 3:
        # Seems like the host is invalid. Just return a path made from whatever we were given.
        return "{}/{}".format(host, renderer)
    if len(renderer_parts) == 2:
        # Renderer is missing the platform. Add it.
        renderer_parts.append(host_parts[-1])
    return "{}/{}".format(" ".join(host_parts), " ".join(renderer_parts))
