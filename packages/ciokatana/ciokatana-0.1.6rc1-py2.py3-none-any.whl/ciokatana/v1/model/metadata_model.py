from ciokatana.v1.model import array_model

PARAM = "metadata"

def create(node):
    node.getParameters().createChildStringArray(PARAM, 0)
    
def get_entries(node):
    return array_model.get_entries(node, PARAM)

def set_entries(node, entries):
    array_model.set_entries(node, PARAM, entries)

def resolve(node):
    """Resolve the metadata field for merging into the payload.
    """
    
    return { "metadata":  dict(get_entries(node))}

