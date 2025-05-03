"""
NAME: ScanAssets
ICON: icon.png
KEYBOARD_SHORTCUT: 
SCOPE:
Scan Assets


"""
from Katana import NodegraphAPI

from ciokatana.v1.model import assets_model

crnode = NodegraphAPI.GetNode("ConductorRender")

assets = assets_model.resolve(crnode)["upload_paths"]
for a in assets:
    print(a)
