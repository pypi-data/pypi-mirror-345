from ciokatana.v1.model import array_model, software_model
from ciocore import data as coredata
from ciocore.package_environment import PackageEnvironment

PARAM = "extraEnvironment"


def create(node):
    node.getParameters().createChildStringArray(PARAM, 0)


def get_entries(node):
    return array_model.get_entries(node, PARAM)


def set_entries(node, entries):
    array_model.set_entries(node, PARAM, entries)


def resolve(node):
    """
    Compose the environment submission sub-object.

    Consists of:
        * Environment provided by the packages (Katana + Arnold / Vray etc.)
        * CONDUCTOR_PATHHELPER = Buggy - turn off by default.
        * Extra environment defined by the user from the corresponding UI
          component.
    """
    env = PackageEnvironment()
    if coredata.valid():
        tree_data = coredata.data()["software"]
        software_paths = software_model.get_paths(node)
        for path in software_paths:
            package = tree_data.find_by_path(path)
            if package:
                env.extend(package)

    extras = [
        {"name": x[0], "value": x[1], "merge_policy": "exclusive" if x[2] else "append"}
        for x in get_entries(node)
    ]
    extras.append(
        {"name": "CONDUCTOR_PATHHELPER", "value": "0", "merge_policy": "exclusive"}
    )

    env.extend(extras)

    return {"environment": dict(env)}
