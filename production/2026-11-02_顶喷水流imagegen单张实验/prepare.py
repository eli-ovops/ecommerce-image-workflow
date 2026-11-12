import bpy,json
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
P=Path(__file__).resolve().parent
S=P.parent/'2026-11-02_391安装仰视单张实验'
bpy.ops.wm.open_mainfile(filepath=str(S/'391-installation.blend'))
sc=bpy.context.scene
pts=[]
for o in bpy.data.objects:
 if o.name.startswith('WATER_'):
  p=o.matrix_world @ o.data.splines[0].bezier_points[0].co
  v=world_to_camera_view(sc,sc.camera,p)
  pts.append(dict(id=o.name,x=v.x*1200,y=(1-v.y)*1200))
  o.hide_render=True
sc.cycles.samples=64;sc.render.filepath=str(P/'dry-product.png')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'dry-product.blend'))
bpy.ops.render.render(write_still=True)
(P/'projected-origins.json').write_text(json.dumps(pts,indent=2))
