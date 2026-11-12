import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parent;O=B/'v007';(O/'renders').mkdir(parents=True,exist_ok=True);(O/'evidence').mkdir(exist_ok=True)
SOURCE=B/'v005/shower_black_clay_v005.blend';bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
Pold=json.loads((B/'parameters-v005.json').read_text())
# Head face is a plane. Fit only original head-front stations185..235 to set its orientation.
xy=[(z,y) for z,y in Pold['front_profile_z_y'] if 185<=z<=235];mx=sum(z for z,y in xy)/len(xy);my=sum(y for z,y in xy)/len(xy)
slope=sum((z-mx)*(y-my) for z,y in xy)/sum((z-mx)**2 for z,y in xy);y0=my+slope*(200-mx)
axis=Vector((0,1,-slope)).normalized();up=Vector((0,slope,1)).normalized();right=Vector((1,0,0));C=Vector((0,y0,200))
P={'version':'v007','source':str(SOURCE),'scope':'Head cylinder, planar face, shallow rear cap; original lower neck/handle unchanged','head_center_mm':list(C),'axis_front_to_back_unit':list(axis),'face_up_unit':list(up),'face_slope_dy_dz':slope,'radius_mm':65,'axial_wall_length_mm':18.5,'edge_round_mm':.4,'rear_dome_depth_mm':7,'side_segments':256,'preserve_original_vertices_z_le_mm':135,'head_root_transition_z_mm':[135,175],'evidence':['user cylindrical-head correction screenshot','P05 head edge','P03/P04 side','P07/P08 oblique'],'uncertainty':'Axial wall18.5 and rear dome7 are visual candidate dimensions, not physical metrology. Overall model still rejected/pending; no whole-model PASS.','routing':Pold['routing']}
(B/'parameters-v007.json').write_text(json.dumps(P,ensure_ascii=False,indent=2))
col=bpy.data.collections['PRODUCT | editable exterior candidate'];old=bpy.data.objects['01 Continuous head-neck-handle shell'];oldpts=[tuple(v.co) for v in old.data.vertices if v.co.z<=.13500001]
mat=bpy.data.materials['Clay - exterior'];pmat=bpy.data.materials['Clay - separate face insert'];bmat=bpy.data.materials['Clay - controls']
def make(name,vs,fs,ma):
 me=bpy.data.meshes.new(name+' mesh');me.from_pydata([tuple(v*.001) for v in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);col.objects.link(ob);ob.data.materials.append(ma)
 for p in ob.data.polygons:p.use_smooth=True
 return ob
def pt(r,a,d):return C+right*(r*math.cos(a))+up*(r*math.sin(a))+axis*d
# Build full head as rotational surface around explicit face normal. Front and rear are distinct surfaces.
N=256;vs=[];fs=[];rings=[]
# Front radial cap: center then ring0. Side wall straight span between ring1 andring2.
ringdefs=[(65-.4,0),(65,.4),(65,18.1),(65-.4,18.5)]
for r,d in ringdefs:
 rings.append(len(vs))
 for j in range(N):vs.append(pt(r,2*math.pi*j/N,d))
for k in range(3):
 for j in range(N):a=k*N+j;b=k*N+(j+1)%N;fs.append((a,b,b+N,a+N))
# shallow back dome: radial rings moving inward, a separate mathematical surface, not inflated cylinder side
for k in range(1,33):
 r=(65-.4)*(1-k/33);d=18.5+7*(1-(r/(65-.4))**2)
 start=len(vs);prev=start-N
 for j in range(N):vs.append(pt(r,2*math.pi*j/N,d))
 for j in range(N):fs.append((prev+j,prev+(j+1)%N,start+(j+1)%N,start+j))
ci=len(vs);vs.append(C+axis*25.5);prev=ci-N
for j in range(N):fs.append((prev+j,prev+(j+1)%N,ci))
# front is a planar triangle fan, so no non-planar NGon can auto-triangulate inconsistently
ci=len(vs);vs.append(C)
for j in range(N):fs.append((j,ci,(j+1)%N))
head=make('01 Head body - true cylindrical wall plus separate shallow rear cap',vs,fs,mat)
# annotate exact component surfaces for viewport inspection
for i,p in enumerate(head.data.polygons):
 if i<3*N:p.use_smooth=True
 elif i>=len(head.data.polygons)-N:p.use_smooth=False
head['cylinder_axis']=list(axis);head['straight_wall_rings_vertex_indices']=[N,2*N];head['straight_wall_length_mm']=17.7
# Preserve original lower body exactly, cut only original head region above175.
NN=128;ov=[Vector(v.co)*1000 for v in old.data.vertices];row_count=sum(1 for k in range(len(ov)//NN) if ov[k*NN].z<=175.0001)
nvs=[p.copy() for p in ov[:row_count*NN]];nfs=[]
def interp(tab,z):
 for a,b in zip(tab,tab[1:]):
  if a[0]<=z<=b[0]:return a[1]+(b[1]-a[1])*(z-a[0])/(b[0]-a[0])
 return tab[0][1] if z<tab[0][0] else tab[-1][1]
for v in nvs:
 z=v.z
 if z>135.00001:
  t=min(1,(z-135)/40);w=t*t*(3-2*t);f=interp(Pold['front_profile_z_y'],z);back=interp(Pold['back_profile_z_y'],z);q=(v.y-f)/(back-f)
  plane=y0+slope*(z-200);target_f=plane+.8;target_b=plane+22
  v.y=(1-w)*v.y+w*(target_f+q*(target_b-target_f))
  if z>155:
   a=(z-155)/20;a=a*a*(3-2*a);v.x*=1-.10*a
# Put the terminal upper-neck cap fully inside the new head, and keep its face behind the planar insert.
for v in nvs:
 if v.z>135.00001:
  local=v-C;rad=(v.x*v.x+local.dot(up)**2)**.5;d=local.dot(axis)
  if rad<64.6:
   if d<.3:v+=axis*(.3-d)*min(1,(v.z-135)/2)
   if v.z>150:
    q=min(1,(v.z-150)/25);q=q*q*(3-2*q);cap=18.5+7*(1-(rad/64.6)**2)-.65;d=(v-C).dot(axis)
    if d>cap:v-=axis*(d-cap)*q
for i in range(row_count-1):
 for j in range(NN):a=i*NN+j;b=i*NN+(j+1)%NN;nfs.append((a,b,b+NN,a+NN))
nfs.append(tuple(reversed(range(NN))));nfs.append(tuple((row_count-1)*NN+j for j in range(NN)))
neck=make('02 Original handle and lower neck - unchanged below135mm',nvs,nfs,mat)
# Avoid even float32 unit-conversion drift in protected lower geometry.
for i,v in enumerate(neck.data.vertices):
 if old.data.vertices[i].co.z<=.13500001:v.co=old.data.vertices[i].co

# Remove only obsolete scene objects in this newly loaded working copy; source .blend stays untouched.
for name in ['01 Continuous head-neck-handle shell','02 Removable face panel - holes pending','03 Central descaling press button | gray clay']:
 ob=bpy.data.objects.get(name)
 if ob:bpy.data.objects.remove(ob,do_unlink=True)
# Face disc planar and triangulated; no curved front(z) dependency.
def disk(name,r,depth,d0,ma):
 vs=[];fs=[]
 for d in [d0,d0+depth]:
  for j in range(N):vs.append(pt(r,2*math.pi*j/N,d))
 c0=len(vs);vs.append(C+axis*d0);c1=len(vs);vs.append(C+axis*(d0+depth))
 for j in range(N):
  j1=(j+1)%N;fs.extend([(j,j1,N+j1,N+j),(j,c0,j1),(N+j,N+j1,c1)])
 ob=make(name,vs,fs,ma)
 for p in ob.data.polygons:p.use_smooth=False
 return ob
face=disk('03 Planar removable face panel',62.6,.8,-.8,pmat)
# central control remains only a plain gray exterior reference on the new planar face.
vs=[];fs=[]
for r,d in [(9,-1.0),(9,-2.0),(6,-3.5),(3,-3.5),(2.8,-1.0)]:
 for j in range(96):vs.append(pt(r,2*math.pi*j/96,d))
for k in range(4):
 for j in range(96):fs.append((k*96+j,k*96+(j+1)%96,(k+1)*96+(j+1)%96,(k+1)*96+j))
ctrl=make('04 Central control aligned to face plane',vs,fs,bmat)
# Pre-render geometry evidence. Side ring difference must be parallel to one axis, constant magnitude.
rd=[];err=[]
for j in range(N):
 a=Vector(head.data.vertices[N+j].co)*1000;b=Vector(head.data.vertices[2*N+j].co)*1000;delta=b-a;rd.append(delta.length);err.append((delta-axis*17.7).length)
newlow=[tuple(v.co) for v in neck.data.vertices if v.co.z<=.13500001]
report={'model':'v007','pre_render_geometry_check':{'ring_pair_count':N,'axis':list(axis),'straight_wall_axial_distance_min_max_mm':[min(rd),max(rd)],'maximum_vector_error_from_axis_times17_7_mm':max(err),'lower_body_original_vertex_count':len(oldpts),'lower_body_current_vertex_count':len(newlow),'lower_body_max_xyz_difference_m':max(max(abs(a[k]-b[k]) for k in range(3)) for a,b in zip(oldpts,newlow)),'face_ngons':sum(len(p.vertices)>4 for p in face.data.polygons),'face_triangle_count':sum(len(p.vertices)==3 for p in face.data.polygons)},'topology':[],'limitations':['Head and root are intersecting exterior components at this local-correction stage; not a manufacturing assembly','Rear cap7mm and axial18.5mm are provisional; hand/camera affects apparent thickness','Only the requested cylindrical sidewall correction is under review; prior whole-model rejection remains']}
# Retain an inspectable hidden construction body with the full corresponding extrusion rings.
construction=bpy.data.collections.new('CONSTRUCTION | cylinder before root union');scene0=bpy.context.scene;scene0.collection.children.link(construction)
proof=head.copy();proof.data=head.data.copy();proof.name='Cylinder construction proof - full coaxial rings';construction.objects.link(proof);proof.hide_render=True;proof.hide_viewport=True
# Exact local union removes internal cap intersections, retaining the actual cylinder exterior.
bpy.context.view_layer.objects.active=head;head.select_set(True)
mod=head.modifiers.new('Local head-root surface union','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=neck
bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(neck,do_unlink=True)
head.name='01 Unified exterior - cylinder head and preserved lower body'
bm=bmesh.new();bm.from_mesh(head.data);bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4]);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(head.data);bm.free()
for p in head.data.polygons:p.use_smooth=True
protected_final=[tuple(v.co) for v in head.data.vertices if v.co.z<=.13500001]
protected_set=set(protected_final);report['post_union_protected_lower_vertices']={'source_count':len(oldpts),'final_count':len(protected_final),'exact_source_vertices_present':sum(p in protected_set for p in oldpts),'all_source_vertices_present_exactly':all(p in protected_set for p in oldpts)}
report['limitations'][0]='Exact head-root union; exterior candidate only, not a manufacturing assembly'
for ob in [head,face]:
 bm=bmesh.new();bm.from_mesh(ob.data);report['topology'].append({'name':ob.name,'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-14 for f in bm.faces)});bm.free()
(O/'evidence/geometry-check.json').write_text(json.dumps(report,indent=2))
scene=bpy.context.scene;scene.render.resolution_x=1000;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=95;scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
cam=scene.camera;cam.data.type='ORTHO';cam.data.ortho_scale=.31
T=Vector((0,.017,.1325))
def camera(angle,target=T,scale=.31,elev=0):
 a=math.radians(angle);cam.location=target+Vector((.7*math.sin(a),-.7*math.cos(a),elev));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
camera(115,Vector((0,.02,.195)),.18,.035)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'shower_black_clay_v007.blend'))
for name,angle,target,scale,elev in [('strict_side',90,T,.31,0),('head_oblique_front',55,Vector((0,.02,.200)),.175,.025),('head_oblique_back',125,Vector((0,.02,.200)),.175,.025)]:
 camera(angle,target,scale,elev);scene.render.filepath=str(O/'renders'/f'{name}.jpg');bpy.ops.render.render(write_still=True)
# Construction proof of separate closed circular rings: isolate head and show same solid cylinder with wire overlay.
for ob in col.objects:ob.hide_render=ob not in [head]
camera(65,Vector((0,.02,.200)),.175,.04);head.show_wire=True;head.show_all_edges=True
scene.render.filepath=str(O/'evidence/head-cylinder-isolated.jpg');bpy.ops.render.render(write_still=True)
print('V007_COMPLETE',O)
