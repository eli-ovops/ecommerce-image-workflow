import bpy,json
from pathlib import Path
p=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(p.parent/'2026-10-30_方案一_三维反射构图/三维方案一.blend'))
s=bpy.context.scene
for o in s.objects:
 if not o.name[:2].isdigit(): print('ENV',o.name,o.type,tuple(o.location),tuple(o.rotation_euler),tuple(o.dimensions))
 elif o.name.startswith(('00','01','02','03','04','05','06','07','08','09')): print('PRODUCT',o.name,tuple(o.location),[m.name for m in o.data.materials])
for m in bpy.data.materials:
 if m.use_nodes:
  print('MAT',m.name,[(n.name,[(i.name,str(i.default_value)) for i in n.inputs if hasattr(i,'default_value') and i.name in ['Base Color','Metallic','Roughness','Strength','Distance','Scale']]) for n in m.node_tree.nodes])
print('CAM',s.camera.name,tuple(s.camera.location),tuple(s.camera.rotation_euler),s.camera.data.ortho_scale,s.camera.data.shift_x,s.camera.data.shift_y)
