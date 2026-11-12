import bpy, json, hashlib, struct
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
p=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(p.parent/'2026-10-30_圆形花洒_完整手柄返修/完整手柄_场景.blend'))
s=bpy.context.scene
objects=[o for o in s.objects if o.type=='MESH' and o.name[:2].isdigit()]
def fingerprint():
 return {o.name:hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in o.data.vertices)).hexdigest() for o in objects}
before=fingerprint()
s.camera.data.ortho_scale=.335
s.camera.data.shift_y=-.01
# Adjust existing reflection sources without changing object meshes or material assignments.
key=bpy.data.objects.get('Large window daylight')
if key: key.data.size=.29;key.data.size_y=.42
fill=bpy.data.objects.get('Neutral right fill')
if fill: fill.data.energy *= .85
back=bpy.data.objects.get('Soft rear edge')
if back: back.data.size=.36
bpy.context.view_layer.update()
coords=[world_to_camera_view(s,s.camera,o.matrix_world @ Vector(c)) for o in objects for c in o.bound_box]
bounds=[min(v.x for v in coords),max(v.x for v in coords),min(v.y for v in coords),max(v.y for v in coords)]
assert min(bounds[0],bounds[2])>.015 and max(bounds[1],bounds[3])<.985, str(bounds)
assert before==fingerprint()
s.render.resolution_x=s.render.resolution_y=1600;s.render.resolution_percentage=100;s.cycles.samples=96
s.render.image_settings.file_format='PNG';s.render.filepath=str(p/'三维方案一_无字.png')
(p/'模型检查.json').write_text(json.dumps({'mesh_hashes_unchanged':True,'product_bounds_normalized':bounds,'note':'bounding-box check only, not physical accuracy; outer nozzles approximate'},ensure_ascii=False,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(p/'三维方案一.blend'))
bpy.ops.render.render(write_still=True)
