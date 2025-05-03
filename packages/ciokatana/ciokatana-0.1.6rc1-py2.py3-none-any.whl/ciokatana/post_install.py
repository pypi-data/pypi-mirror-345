import os
import sys
import errno
import shutil
import glob



def fslash(path):
    return path.replace("\\", "/")

PLATFORM = sys.platform
CIO_DIR = fslash(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOME = fslash(os.path.expanduser("~"))


KATANA_USER_RESOURCE_DIR = os.environ.get("KATANA_USER_RESOURCE_DIRECTORY", os.path.join(HOME, ".katana"))
SUPERTOOL_INIT_FILE = fslash(os.path.join(KATANA_USER_RESOURCE_DIR, "SuperTools", "ConductorRender", "__init__.py"))

SHELF_DEST_DIR = fslash(os.path.join(KATANA_USER_RESOURCE_DIR, "Shelves", "Conductor"))
SHELF_SOURCE_DIR  = os.path.join(CIO_DIR, "ciokatana", "shelf_items")

    

INIT_CONTENT = """
import sys
CIO_DIR = "{}"
sys.path.insert(1, CIO_DIR)

import logging
log = logging.getLogger('__init__')

try:
    from ciokatana.v1 import setup
except Exception as exception:
    log.exception("Error importing ConductorRender Super Tool Python package: {{}}".format(exception))
else:
    PluginRegistry = [("SuperTool", 2, "ConductorRender",
                      (setup.ConductorRenderNode,
                       setup.GetEditor))]

""".format(CIO_DIR)

def main():
    if not PLATFORM.startswith(("win", "linux")):
        sys.stderr.write("Unsupported platform: {}".format(PLATFORM))
        sys.exit(1)

    ensure_directory(os.path.dirname(SUPERTOOL_INIT_FILE))

    with open(SUPERTOOL_INIT_FILE, "w") as f:
        f.write(INIT_CONTENT)

    sys.stdout.write("Wrote ConductorRender init file: {}\n".format(SUPERTOOL_INIT_FILE))
    sys.stdout.write("Completed Katana super tool setup!\n")
    

    shelf_files = glob.glob(os.path.join(SHELF_SOURCE_DIR, '*.py'))
    ensure_directory(SHELF_DEST_DIR)
    
    for shelf in shelf_files:
        shutil.copy(shelf, SHELF_DEST_DIR)
        
    sys.stdout.write("Completed Conductor shelf setup!\n")

def ensure_directory(directory):
    try:
        os.makedirs(directory)
    except OSError as ex:
        if ex.errno == errno.EEXIST and os.path.isdir(directory):
            pass
        else:
            raise

if __name__ == "__main__":
    main()
