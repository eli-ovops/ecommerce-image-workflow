import bpy,json,hashlib,struct
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parent
parent=P.parent.parent/'399-preview.blend';uv=P.parent/'399-preview.blend'
bpy.ops.wm.open_mainfile(filepath=str(parent));s=bpy.context.scene
lights={}
for o in s.objects:
 if o.type=='LIGHT':
  lights[o.name]={'matrix':[list(r) for r in o.matrix_world],'energy':o.data.energy,'color':list(o.data.color),'shape':o.data.shape,'size':o.data.size,'size_y':o.data.size_y}
bg=next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND')
world={'color':list(bg.inputs[0].default_value),'strength':bg.inputs[1].default_value}
exposure=s.view_settings.exposure
bpy.ops.wm.open_mainfile(filepath=str(uv));s=bpy.context.scene
def fingerprint():
 h=hashlib.sha256()
 for o in sorted(bpy.data.objects['Product_RIG_RIGID_ONLY'].children,key=lambda o:o.name):
  h.update(o.name.encode());h.update(str(list(map(list,o.matrix_basis))).encode())
  if o.type=='MESH':
   for v in o.data.vertices:h.update(struct.pack('3f',*v.co))
   for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 return h.hexdigest()
def material_fingerprint():
 m=bpy.data.objects['Recessed_panel_with_true_through_holes'].data.materials[0];h=hashlib.sha256()
 for n in m.node_tree.nodes:
  h.update((n.name+n.bl_idname).encode())
  for i in n.inputs:
   if hasattr(i,'default_value'):h.update(str(i.default_value[:] if hasattr(i.default_value,'__len__') else i.default_value).encode())
  if n.type=='TEX_IMAGE':h.update(bytes(n.image.packed_file.data))
 for l in m.node_tree.links:h.update(str((l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)).encode())
 return h.hexdigest()
before=fingerprint();mat_before=material_fingerprint();camera_before=[list(r) for r in s.camera.matrix_world]
assert {o.name for o in s.objects if o.type=='LIGHT'}==set(lights)
for name,d in lights.items():
 o=bpy.data.objects[name];o.matrix_world=Matrix(d['matrix'])
 for k in ['energy','color','shape','size','size_y']:setattr(o.data,k,d[k])
bg=next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=world['color'];bg.inputs[1].default_value=world['strength'];s.view_settings.exposure=exposure
assert fingerprint()==before and material_fingerprint()==mat_before
assert camera_before==[list(r) for r in s.camera.matrix_world]
report={'parent_scene':str(parent),'parent_sha256':hashlib.sha256(parent.read_bytes()).hexdigest(),'uv_scene':str(uv),'uv_sha256':hashlib.sha256(uv.read_bytes()).hexdigest(),'restored_lights':lights,'restored_world':world,'restored_exposure':exposure,'geometry_and_transforms_unchanged':True,'geometry_sha256':before,'panel_material_and_packed_texture_unchanged':True,'panel_material_sha256':mat_before,'preview_camera_unchanged':True,'scope':'Lighting isolation only; no material, texture, geometry, camera or extra light edits.'}
(P/'isolation-check.json').write_text(json.dumps(report,indent=2))
s.render.filepath=str(P/'399-preview.jpg');bpy.ops.wm.save_as_mainfile(filepath=str(P/'399-preview.blend'));bpy.ops.render.render(write_still=True)
rig=bpy.data.objects['Product_RIG_RIGID_ONLY'];cam=s.camera;cam.location=rig.matrix_world@Vector((-.075,.02,.23));target=rig.matrix_world@Vector((-.075,.02,.007));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.085;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=80;s.render.filepath=str(P/'399-detail.jpg');bpy.ops.render.render(write_still=True)
