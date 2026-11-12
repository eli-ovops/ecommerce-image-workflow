import bpy,json,hashlib,struct,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
p=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(p.parent/'2026-10-30_方案一_三维反射构图/三维方案一.blend'))
s=bpy.context.scene
obs=[o for o in s.objects if o.type=='MESH' and o.name[:2].isdigit()]
def fp():
 return {o.name:hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in o.data.vertices)+b''.join(struct.pack('<I',i) for f in o.data.polygons for i in f.vertices)+str(tuple(tuple(x) for x in o.matrix_world)).encode()).hexdigest() for o in obs}
before=fp()
# Native scene changes only. Product mesh, topology, transforms and hole positions stay unchanged.
s.camera.data.ortho_scale=.30
s.camera.data.shift_x=0;s.camera.data.shift_y=0
bpy.context.view_layer.update()
def bounds():
 pts=[world_to_camera_view(s,s.camera,o.matrix_world@Vector(c)) for o in obs for c in o.bound_box]
 return [min(v.x for v in pts),max(v.x for v in pts),min(v.y for v in pts),max(v.y for v in pts)]
b=bounds();s.camera.data.shift_x=(b[0]+b[1])/2-.5;s.camera.data.shift_y=(b[2]+b[3])/2-.5
# Larger separation between bright window and dark reflection card, with no pixel retouching.
window=bpy.data.objects['Large physical window reflection'];window.scale.x *= .62
bpy.ops.mesh.primitive_plane_add(size=1,location=(-.025,.24,.37))
card=bpy.context.object;card.name='Astra dark reflection card';card.rotation_euler=(Vector((-.04,.05,.04))-card.location).to_track_quat('Z','Y').to_euler();card.scale=(.055,.44,1)
mat=bpy.data.materials.new('Astra charcoal card');mat.diffuse_color=(.025,.025,.025,1);mat.use_nodes=True
bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.025,.025,.025,1);bs.inputs['Roughness'].default_value=.8;card.data.materials.append(mat);card.visible_camera=False
silver=bpy.data.materials['Studio silver - optical approximation'].node_tree.nodes['Principled BSDF'];silver.inputs['Roughness'].default_value=.12
fill=bpy.data.objects['Neutral right fill'];fill.data.energy*=.75
key=bpy.data.objects['Large window daylight'];key.data.size=.32;key.data.size_y=.46
bpy.context.view_layer.update();b=bounds();assert min(b[0],b[2])>.045 and max(b[1],b[3])<.955,b
assert before==fp()
final='--final' in sys.argv
s.render.resolution_x=s.render.resolution_y=1600 if final else 800;s.render.resolution_percentage=100;s.cycles.samples=128 if final else 48
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=96;s.render.filepath=str(p/('方案一_Astra_无字审阅.jpg' if final else 'draft.jpg'))
(p/'geometry-audit.json').write_text(json.dumps({'product_mesh_topology_transforms_unchanged':before==fp(),'product_fingerprints':before,'bounding_box_normalized':b,'actual_model':'UNKNOWN','requested_model':'gpt-6-astra','requested_effort':'medium'},ensure_ascii=False,indent=2))
if final:bpy.ops.wm.save_as_mainfile(filepath=str(p/'方案一_Astra_可编辑.blend'))
bpy.ops.render.render(write_still=True)
