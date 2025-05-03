"""
NAME: ReloadConductorRender
ICON: icon.png
KEYBOARD_SHORTCUT: 
SCOPE:
Reload Conductor Render

"""
import importlib
from ciokatana.v1 import reloader
importlib.reload(reloader)

reloader.reload()
console_print("reloaded")