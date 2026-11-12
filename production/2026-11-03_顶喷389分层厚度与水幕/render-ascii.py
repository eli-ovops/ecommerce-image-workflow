from pathlib import Path
import bpy,json,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;S=P.parent/'2026-11-02_391\u5b89\u88c5\u4ef0\u89c6\u5355\u5f20\u5b9e\u9a8c';N=P/'native';N.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'391-installation.blend'));sc=bpy.context.scene
for o in bpy.data.objects:
 if o.name.startswith('WATER_'):o.hide_render=True
sc.render.resolution_x=1800;sc.render.resolution_y=1800;sc.render.resolution_percentage=100;sc.cycles.samples=64;sc.render.film_transparent=True
sc.render.image_settings.color_mode='RGBA';sc.render.filepath=str(N/'installed-dry.png');bpy.ops.wm.save_as_mainfile(filepath=str(N/'installed-dry.blend'));bpy.ops.render.render(write_still=True)
housing=bpy.data.objects['Housing_300x200x20'];coords=[housing.matrix_world@Vector(x) for x in housing.bound_box];local=[Vector(x) for x in housing.bound_box]
rig=bpy.data.objects['Product_RIG_RIGID_ONLY'];projections=[]
for p in json.loads((S/'water-origins.json').read_text()):
 v=world_to_camera_view(sc,sc.camera,rig.matrix_world@Vector((p['x'],p['y'],.0091)));projections.append(dict(id=p['id'],x=v.x*1800,y=(1-v.y)*1800))
report=dict(housing_local_bbox=[max(v[i] for v in local)-min(v[i] for v in local) for i in range(3)],housing_scale=list(housing.scale),source=str(S/'391-installation.blend'),photo_method=json.loads((S/'photo-method.json').read_text()),anchors=projections,water_disabled=True)
(N/'geometry-and-projection.json').write_text(json.dumps(report,indent=2))
# Static product from same geometry and same single photographic face.
for o in bpy.data.objects:
 if o.type=='CURVE':o.hide_render=True
rig.location=(0,0,0);rig.rotation_euler=(0,0,math.radians(90))
sc.camera.location=(.16,-.08,.63);sc.camera.rotation_euler=(Vector((0,0,0))-sc.camera.location).to_track_quat('-Z','Y').to_euler();sc.camera.data.ortho_scale=.38
for o in bpy.data.objects:
 if o.type=='LIGHT':
  o.location.z-=.5
  o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
sc.render.resolution_x=1000;sc.render.resolution_y=1400;sc.render.filepath=str(N/'static-dry.png');bpy.ops.wm.save_as_mainfile(filepath=str(N/'static-dry.blend'));bpy.ops.render.render(write_still=True)
