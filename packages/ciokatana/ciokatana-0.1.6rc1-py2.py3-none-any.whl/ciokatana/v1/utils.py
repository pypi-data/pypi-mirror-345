from Katana import NodegraphAPI
from ciopath.gpath import Path
from ciocore.hardware_set import HardwareSet
from ciokatana.v1 import const as k
from contextlib import contextmanager

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

@contextmanager
def wait_cursor():
    """Context manager to wrap in a wait cursor."""
    QApplication.setOverrideCursor(Qt.WaitCursor)
    try:
        yield
    finally:
            QApplication.restoreOverrideCursor()



def get_context(node):
    """A dictionary to facilitate string formatting.

    For exammple, the task template can be formatted with the context.
    """
    projectfile = NodegraphAPI.NodegraphGlobals.GetProjectFile()
    if projectfile:
        projectfile = Path(projectfile).fslash(with_drive=False)

    return {
        "projectfile": projectfile or k.NOT_SAVED,
        "rendernode": "MyRenderNode",
    }

def unconnected_hardware():
    
    return HardwareSet([ {
        "cores": 0,
        "memory": 0,
        "description":  k.NOT_CONNECTED,
        "name":  k.NOT_CONNECTED,
        "operating_system": "linux",
    }])
