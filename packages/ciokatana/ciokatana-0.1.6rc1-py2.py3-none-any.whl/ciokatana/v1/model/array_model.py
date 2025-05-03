import json

"""
Entries are stored in a string array parameter.

Each entry contains the JSON-stringified contents of each input element.
They are stringified on the way in, and parsed on the way out.

This allows us to store arbitrary data in each list element.
"""

def get_entries(node, param_name):
    param = node.getParameter(param_name)
    
    num = param.getNumChildren()
    entries = []
    for i in range(num):
        entries.append(json.loads(param.getChildByIndex(i).getValue(0)))
    return entries

def set_entries(node, param_name, entries):
    num = len(entries)
    param = node.getParameter(param_name)
    param.resizeArray(num)
    for i, entry in enumerate(entries):
        param.getChildByIndex(i).setValue(json.dumps(entry), 0)