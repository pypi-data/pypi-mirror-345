from ciocore import data as coredata
from ciokatana.v1 import const as k

INSTANCE_TYPE_PARAM = "instanceType"
PREEMPTIBLE_PARAM = "preemptible"
RETRIES_PARAM = "retries"


def create(node):
    """Create the parameters.
    
    To choose the initial instance_type, we look for the first instance type
    with more than 2 cores and more than 8GB of memory. If none is found, we
    just use the first one we find.
    """

    instance_type = _valid_value(k.NOT_CONNECTED)
    node.getParameters().createChildString(INSTANCE_TYPE_PARAM, instance_type)
    node.getParameters().createChildNumber(PREEMPTIBLE_PARAM, 1)
    node.getParameters().createChildNumber(RETRIES_PARAM, 1)

def set_value(node, value):
    """Setter ensures that the value is valid, or easy to spot if not."""
    valid_value = _valid_value(value)
    node.getParameter(INSTANCE_TYPE_PARAM).setValue(valid_value, 0)

def get_value(node):
    """Getter ensures that the value is valid, or easy to spot if not."""
    value = node.getParameter(INSTANCE_TYPE_PARAM).getValue(0)
    valid_value = _valid_value(value)
    if valid_value != value:
        set_value(node, valid_value)
        return valid_value
    return value

def resolve(node):
    """Resolve the payload for the node."""
    result = {
        "instance_type": get_value(node),
        "preemptible": node.getParameter(PREEMPTIBLE_PARAM).getValue(0) > 0,
    }
    retries =  int(node.getParameter(RETRIES_PARAM).getValue(0))
    if result["preemptible"] and retries:
        result.update({"autoretry_policy": {"preempted": {"max_retries": retries}}})
    return result

def _valid_value(value):
    """
    Find a valid instance type based on the current value.
    
    If no connection, then the current value is considered valid since wee can't check.
    """
    if not coredata.valid():
        return value
    hardware = coredata.data()["instance_types"]
    if hardware.find(value):
        return value
    result = hardware.find_first( lambda x: float(x["cores"]) > 2 and float(x["memory"]) > 8 )
    if result:
        return result["name"]
    return hardware.find_first( lambda x: True )["name"]