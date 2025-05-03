from ciocore import data as coredata
from ciokatana.v1 import const as k

PROJECT_PARAM = "conductorProject"

def create(node):
    """Create the project parameter on the node.
    
    If we already connected to conductor, use the first project in the list.
    """
    project = _valid_value(k.NOT_CONNECTED)
    node.getParameters().createChildString(PROJECT_PARAM, project)

# accessors
def get_value(node):
    """Getter ensures that the value is valid, or easy to spot if not."""
    value = node.getParameter(PROJECT_PARAM).getValue(0)
    valid_value = _valid_value(value)
    if valid_value != value:
        set_value(node, valid_value)
        return valid_value    
    return value

def set_value(node, value):
    valid_value = _valid_value(value)
    node.getParameter(PROJECT_PARAM).setValue(valid_value, 0)

def resolve(node):
    """Resolve the payload field for the project parameter."""
    return {"project": get_value(node)}


def _valid_value(value):
    """Return a valid value based on the input value."""
    if not coredata.valid():
        # we don't know if the current value is valid, so just return the current value.
        return value
    projects = coredata.data()["projects"]
    if value not in projects:
        return projects[0]
    return value
