import bpy,json
from pathlib import Path
B=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(B/'sources/baseline.blend'))
r={}
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name[:2].isdigit():
  r[o.name]={'scale':list(o.scale),'bounds':[list(o.bound_box[0]),list(o.bound_box[6])],'materials':[]}
  for mat in o.data.materials:
   if mat:r[o.name]['materials'].append({'name':mat.name,'nodes':[{'name':n.name,'type':n.type,'values':{i.name:list(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value for i in n.inputs if hasattr(i,'default_value') and i.type in ['VALUE','RGBA','VECTOR']}} for n in mat.node_tree.nodes]})
(B/'source-material-probe.json').write_text(json.dumps(r,indent=2))
