import bpy
from pathlib import Path
B=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(B/'sources/baseline.blend'))
for o in bpy.context.scene.objects:
 print('OBJECT',o.name,list(o.location))
 if o.type=='MESH' and o.name.startswith(('01 ','02 ')):
  m=o.data.materials[0]
  for n in m.node_tree.nodes:
   print(n.name,n.type,[(s.name,str(s.default_value)) for s in n.inputs if hasattr(s,'default_value') and s.name in ['Scale','Strength','Distance','Roughness','Base Color','Metallic']])
