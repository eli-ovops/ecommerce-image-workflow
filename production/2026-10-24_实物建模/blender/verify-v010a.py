import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
B=Path(__file__).parent;O=B/'v010a';F=O/'shower_black_clay_v010a.blend';name='01 Unified exterior - shared cylinder and neck boundary'
def mesh_read(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));o=bpy.data.objects[name];verts=[tuple(v.co) for v in o.data.vertices];edges=[tuple(e.vertices) for e in o.data.edges];bm=bmesh.new();bm.from_mesh(o.data)
 r={'vertices':len(verts),'faces':len(o.data.polygons),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-14 for f in bm.faces)};bm.free();profiles=[]
 for zmm in [125,130,135,140,145,150,155,160,165,170,180,200,220,240]:
  z=zmm*.001;ys=[]
  for ia,ib in edges:
   a=verts[ia];b=verts[ib]
   if min(a[2],b[2])<=z<=max(a[2],b[2]) and abs(b[2]-a[2])>1e-10:
    t=(z-a[2])/(b[2]-a[2]);ys.append((a[1]+t*(b[1]-a[1]))*1000)
  profiles.append({'world_z_mm':zmm,'projected_front_min_y_mm':min(ys),'projected_back_max_y_mm':max(ys)})
 return verts,r,profiles
new,r,np=mesh_read(F);old,orr,op=mesh_read(B/'v009/shower_black_clay_v009.blend');axis=Vector((0,.9912921786308289,.13168083131313324));deltas=[]
for j in range(193):deltas.append((Vector(new[15*193+j])-Vector(new[193+j]))*1000)
lower=[i for i,v in enumerate(old) if v[2]<=.13500001];changed=[i for i,(a,b) in enumerate(zip(old,new)) if a!=b]
r.update({'version':'v010a','successfully_reopened':True,'blender':bpy.app.version_string,'blend_sha256':hashlib.sha256(F.read_bytes()).hexdigest(),'compare_source':'v009','cylindrical_wall_vertices':3281,'all_wall_coordinates_exactly_unchanged':new[:3281]==old[:3281],'protected_lower_vertices':len(lower),'all_lower_coordinates_exactly_unchanged':all(new[i]==old[i] for i in lower),'changed_vertices':len(changed),'changed_vertex_world_z_range_mm':[min(new[i][2] for i in changed)*1000,max(new[i][2] for i in changed)*1000],'corresponding_ring_pairs':193,'axis':list(axis),'ring_axial_projection_mm_min_max':[min(d.dot(axis) for d in deltas),max(d.dot(axis) for d in deltas)],'v009_actual_projected_mesh_envelope':op,'v010a_actual_projected_mesh_envelope':np,'limits':'Mesh construction comparison only, not calibrated photo fit or physical millimeter accuracy.'})
(O/'evidence/reopen-and-preservation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in r.items() if not isinstance(v,list)},ensure_ascii=False))
