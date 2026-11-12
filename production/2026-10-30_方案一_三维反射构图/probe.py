import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from pathlib import Path
p=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(p.parent/'2026-10-30_圆形花洒_完整手柄返修/完整手柄_场景.blend'))
s=bpy.context.scene
obs=[o for o in s.objects if o.type=='MESH' and o.name[:2].isdigit()]
print('PRODUCT',[(o.name,o.hide_render) for o in obs])
coords=[world_to_camera_view(s,s.camera,o.matrix_world @ Vector(c)) for o in obs for c in o.bound_box]
print('BOUNDS',min(a.x for a in coords),max(a.x for a in coords),min(a.y for a in coords),max(a.y for a in coords))
print('LIGHTS',[(o.name, o.type) for o in s.objects if o.type=='LIGHT'])
