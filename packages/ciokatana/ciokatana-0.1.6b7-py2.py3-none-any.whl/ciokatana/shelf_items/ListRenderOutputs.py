"""
NAME: ListRenderOutputs
ICON: icon.png
KEYBOARD_SHORTCUT: 
SCOPE:
List Render Outputs


"""
from Katana import NodegraphAPI, FarmAPI


from ciokatana.v1.model import jobs_model 

nodes = NodegraphAPI.GetAllSelectedNodes()

for node in nodes:
    outputs = jobs_model.get_outputs(node)
    print("*"*30, node.getName(), "*"*30)
    for output in outputs:
        print(output)
    print("*"*30)
 


