import bpy
from pathlib import Path
B=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(B/'structure-master.blend'))
for o in bpy.context.scene.objects:
 if o.type=='MESH': print(o.name, len(o.data.vertices),list(o.location),[(m.name,m.type) for m in o.modifiers])
