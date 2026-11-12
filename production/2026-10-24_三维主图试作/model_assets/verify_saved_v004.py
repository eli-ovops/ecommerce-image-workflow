import bpy,hashlib,struct,json
from pathlib import Path
O=Path(__file__).resolve().parent;ROOT=O.parents[2];source=ROOT/'production/2026-10-24_实物建模/blender/v010a/shower_black_clay_v010a.blend';target=O/'silver_product_v004.blend';name='01 Unified exterior - shared cylinder and neck boundary'
def read(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));o=bpy.data.objects[name];h=hashlib.sha256()
 for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
 for p in o.data.polygons:h.update(struct.pack('<%di'%len(p.vertices),*p.vertices))
 return h.hexdigest(),len(o.data.vertices),len(o.data.polygons),[list(row) for row in o.matrix_world]
a,vc,pc,ma=read(source);b,nc,nf,mb=read(target);cam=bpy.context.scene.camera
files=json.loads((ROOT/'products/主推花洒/银色/manifest.json').read_text())['files'][:5]
inputs=[{'id':f['id'],'path':str(ROOT/f['project_path']),'sha256':hashlib.sha256((ROOT/f['project_path']).read_bytes()).hexdigest(),'manifest_sha256_match':hashlib.sha256((ROOT/f['project_path']).read_bytes()).hexdigest()==f['sha256']} for f in files]
r={'source_model':str(source),'source_model_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'render_model':str(target),'render_model_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'source_geometry_sha256':a,'saved_geometry_sha256':b,'body_geometry_unchanged':a==b and ma==mb,'body_world_transform_unchanged':ma==mb,'body_world_transform':mb,'body_vertices':nc,'body_faces':nf,'actual_saved_file_reopened':True,'silver_inputs':inputs,'front3q_camera':{'location':list(cam.location),'euler_xyz_radians':list(cam.rotation_euler),'type':cam.data.type,'ortho_scale_m':cam.data.ortho_scale},'renderer':bpy.context.scene.render.engine,'samples':bpy.context.scene.cycles.samples,'film_transparent':bpy.context.scene.render.film_transparent,'packed_referenced_images':[{'name':im.name,'packed':bool(im.packed_file)} for im in bpy.data.images if im.source=='FILE'],'limits':['Geometry preservation is proven; SKU photographic equivalence not claimed','Pure dry product renders; no waterflow or skin check applies','No interface standard or physical material certification']}
(O/'saved-model-verification-v004.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print('SAVED_BODY_UNCHANGED',r['body_geometry_unchanged'])
