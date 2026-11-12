import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
B=Path(__file__).parent;O=B/'v009';F=O/'shower_black_clay_v009.blend'
bpy.ops.wm.open_mainfile(filepath=str(F));ob=bpy.data.objects['01 Unified exterior - shared cylinder and neck boundary'];p=json.loads((B/'parameters-v009.json').read_text());axis=Vector(p['axis_front_to_back_unit']);C=Vector(p['head_center_mm']);up=Vector(p['face_up_unit'])
r=[];err=[];samples=[]
for j in range(193):
 a=ob.data.vertices[193+j].co*1000;b=ob.data.vertices[15*193+j].co*1000;delta=b-a;r.append(delta.dot(axis));err.append((delta-axis*17.7).length)
 if j%24==0:samples.append({'angle_index':j,'front_world_mm':list(a),'back_world_mm':list(b),'delta_mm':list(delta)})
newlow={tuple(v.co) for v in ob.data.vertices if v.co.z<=.13500001};bm=bmesh.new();bm.from_mesh(ob.data)
report={'file':str(F),'sha256':hashlib.sha256(F.read_bytes()).hexdigest(),'blender':bpy.app.version_string,'successfully_reopened':True,'body_vertices':len(ob.data.vertices),'body_faces':len(ob.data.polygons),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-14 for f in bm.faces),'axis_projected_straight_wall_mm_min_max':[min(r),max(r)],'max_delta_vector_error_mm':max(err),'sampled_corresponding_ring_points':samples};bm.free()
# Render actual saved model with geometry-domain grays, for construction inspection only.
for name,colr in [('Cylinder wall domain',(.70,.70,.70,1)),('Planar front domain',(.48,.48,.48,1)),('Shallow rear cap domain',(.36,.36,.36,1))]:
 ma=bpy.data.materials.new(name);ma.diffuse_color=colr;ob.data.materials.append(ma)
for i,face in enumerate(ob.data.polygons):
 if i<3072:face.material_index=1
 elif i<3312:face.material_index=2
 elif i<9312:face.material_index=3
scene=bpy.context.scene;scene.render.filepath=str(O/'evidence/construction-domains.jpg');bpy.ops.render.render(write_still=True)
# Original blend is only read, never saved.
bpy.ops.wm.open_mainfile(filepath=str(B/'v005/shower_black_clay_v005.blend'));old=bpy.data.objects['01 Continuous head-neck-handle shell'];oldlow={tuple(v.co) for v in old.data.vertices if v.co.z<=.13500001};report['protected_lower_vertices']={'source_count':len(oldlow),'all_present_exactly':oldlow.issubset(newlow),'new_lower_count':len(newlow)}
scene=bpy.context.scene;scene.render.resolution_x=1000;scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=95;cam=scene.camera;target=Vector((0,.02,.200));a=math.radians(55);cam.location=target+Vector((.7*math.sin(a),-.7*math.cos(a),.025));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.175;scene.render.filepath=str(O/'evidence/v005-same-camera-before.jpg');bpy.ops.render.render(write_still=True)
(O/'evidence/reopen-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('REOPEN_AND_SOURCE_COORDINATE_CHECK',report['protected_lower_vertices'])
