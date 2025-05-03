from Katana import FarmAPI, NodegraphAPI
from ciokatana.v1.Node import ConductorRenderNode
from ciokatana.v1.dialog import ConductorRenderDialog 
from ciokatana.v1 import utils
from ciokatana.v1 import const as k
import UI4

def GetEditor():
    from .Editor import ConductorRenderEditor
    return ConductorRenderEditor


def on_conductor_menu(reset=False):

    if reset:
        existing = NodegraphAPI.GetAllNodesByType(
           k.CONDUCTOR_RENDER_NODE_TYPE, includeDeleted=False
        )
        for node in existing:
            node.delete()

    
    global conductorRenderDialog
    # if the qdialog exists, delete it
    try:
        conductorRenderDialog.close()
    except:
        pass

    with utils.wait_cursor():
        conductor_node = ConductorRenderNode.singleton_factory()

    # Register the list of render nodes according to the current scope (all|selected|single)
    render_nodes = [n for n in FarmAPI.GetNodeList() if n.getType() == "Render"]
    if not render_nodes:
        UI4.Widgets.MessageBox.Warning(
            "Message", "No render nodes found. Try deselecting all nodes and try again."
        )
        return

    ConductorRenderNode.register_render_nodes(conductor_node, render_nodes)

    conductorRenderDialog = ConductorRenderDialog(conductor_node)
    conductorRenderDialog.resize(800, 800)
    conductorRenderDialog.show()

def add_farm_settings():
    """Add farm settings to all Render nodes."""
    scene_range = FarmAPI.GetSceneFrameRange()
    scene_range_spec = "{start}-{end}x1".format(**scene_range)

    FarmAPI.AddFarmSettingNumber(
        name="conductorOverrides",
        defaultValue=0,
        hints={"widget": "checkBox", "constant": "True"},
    )
    FarmAPI.AddFarmSettingString(
        name="conductorFrameSpec",
        defaultValue=scene_range_spec,
        hints={"constant": "True"},
    )
    FarmAPI.AddFarmSettingString(
        name="conductorScoutSpec", defaultValue="fml:3", hints={"constant": "True"}
    )
    FarmAPI.AddFarmSettingNumber(
        name="conductorChunkSize",
        defaultValue=1,
        hints={"int": "True", "constant": "True"},
    )


add_farm_settings()
FarmAPI.AddFarmMenuOption("Conductor", lambda: on_conductor_menu())
FarmAPI.AddFarmMenuOption("Reset Conductor", lambda: on_conductor_menu(reset=True))
FarmAPI.AddFarmPopupMenuOption("Conductor", on_conductor_menu)
