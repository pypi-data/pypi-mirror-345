"""Model to hold the expanded state of the sections."""


def create(node):
    """Create the parameter."""
    params = node.getParameters()

    open_sections = ["GeneralSection", "HardwareSection", "SoftwareSection"]
    closed_sections = [
        "JobsSection",
        "AssetsSection",
        "EnvironmentSection",
        "MetadataSection",
        "AdvancedSection",
    ]

    for class_name in open_sections:
        param_name = "{}Expanded".format(class_name)
        params.createChildNumber(param_name, 1)

    for class_name in closed_sections:
        param_name = "{}Expanded".format(class_name)
        params.createChildNumber(param_name, 0)


def get_section_state(node, class_name):
    """Get the stored section expanded state."""
    param_name = "{}Expanded".format(class_name)
    params = node.getParameters()
    return params.getChild(param_name).getValue(0)


def set_section_state(node, value, class_name):
    """Set the stored section expanded state."""
    param_name = "{}Expanded".format(class_name)
    params = node.getParameters()
    params.getChild(param_name).setValue(value, 0)
