import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parent;O=B/'v010a';(O/'renders').mkdir(parents=True,exist_ok=True);(O/'evidence').mkdir(exist_ok=True)
SOURCE=B/'v005/shower_black_clay_v005.blend';bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
Pold=json.loads((B/'parameters-v005.json').read_text())
# Head face is a plane. Fit only original head-front stations185..235 to set its orientation.
xy=[(z,y) for z,y in Pold['front_profile_z_y'] if 185<=z<=235];mx=sum(z for z,y in xy)/len(xy);my=sum(y for z,y in xy)/len(xy)
slope=sum((z-mx)*(y-my) for z,y in xy)/sum((z-mx)**2 for z,y in xy);y0=my+slope*(200-mx)
axis=Vector((0,1,-slope)).normalized();up=Vector((0,slope,1)).normalized();right=Vector((1,0,0));C=Vector((0,y0,200))
P={'version':'v010a','source':str(SOURCE),'scope':'Local rear cap and upper neck continuity correction; cylindrical wall and lower body unchanged','head_center_mm':list(C),'axis_front_to_back_unit':list(axis),'face_up_unit':list(up),'face_slope_dy_dz':slope,'radius_mm':65,'axial_wall_length_mm':18.5,'edge_round_mm':.4,'lower_rear_envelope':'lower rear center follows recorded long profile; upper rear C1 cubic continuation to fixed circular rim; cylindrical ring unchanged','side_segments':256,'preserve_original_vertices_z_le_mm':135,'head_root_transition_z_mm':[135,175],'evidence':['user cylindrical-head correction screenshot','P05 head edge','P03/P04 side','P07/P08 oblique'],'uncertainty':'Axial wall18.5 and revised rear envelope are visual candidate dimensions, not physical metrology. Overall model still rejected/pending; no whole-model PASS.','routing':Pold['routing']}
(B/'parameters-v010a.json').write_text(json.dumps(P,ensure_ascii=False,indent=2))
col=bpy.data.collections['PRODUCT | editable exterior candidate'];old=bpy.data.objects['01 Continuous head-neck-handle shell'];oldpts=[tuple(v.co) for v in old.data.vertices if v.co.z<=.13500001]
mat=bpy.data.materials['Clay - exterior'];pmat=bpy.data.materials['Clay - separate face insert'];bmat=bpy.data.materials['Clay - controls']
def make(name,vs,fs,ma):
 me=bpy.data.meshes.new(name+' mesh');me.from_pydata([tuple(v*.001) for v in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);col.objects.link(ob);ob.data.materials.append(ma)
 for p in ob.data.polygons:p.use_smooth=True
 return ob
def pt(r,a,d):return C+right*(r*math.cos(a))+up*(r*math.sin(a))+axis*d

# Shared topology, no Boolean: cylinder major arc, planar front disc, clipped shallow rear cap,
# and a neck patch sharing their actual boundary indices.
N=256;R=65.;re=64.6;alpha=math.asin(35/R);M=192;K=48
angles=[-alpha+(math.pi+2*alpha)*j/M for j in range(M+1)]
vs=[];fs=[]
def add(v):vs.append(v);return len(vs)-1
def quad(a,b,c,d):fs.append((a,b,c,d))
wall=[]
for k in range(17):
 d=0 if k==0 else 18.5 if k==16 else .4+(k-1)*17.7/14
 r=re if k in (0,16) else R
 wall.append([add(pt(r,a,d)) for a in angles])
for k in range(16):
 for j in range(M):quad(wall[k][j],wall[k][j+1],wall[k+1][j+1],wall[k+1][j])
# Minor front arc connects left to right around bottom. Share endpoints.
minor=[wall[0][-1]]+[add(pt(re,math.pi+alpha+(math.pi-2*alpha)*j/K,0)) for j in range(1,K)]+[wall[0][0]]
front_boundary=wall[0]+minor[1:-1];ci=add(C)
for j,a in enumerate(front_boundary):fs.append((a,front_boundary[(j+1)%len(front_boundary)],ci))
front_faces=set(range(16*M,len(fs)))
# Clipped rear shallow dome. The cut chord is the actual neck attachment, no hidden cap.
cutv=-re*math.sin(alpha);cutx=re*math.cos(alpha)
def interp_profile(tab,z):
 for a,b in zip(tab,tab[1:]):
  if a[0]<=z<=b[0]:return a[1]+(b[1]-a[1])*(z-a[0])/(b[0]-a[0])
 return tab[0][1] if z<tab[0][0] else tab[-1][1]
def rear_axis_target(v):
 # Use the recorded long rear profile to bridge the new lower rear cap to the preserved neck.
 d=30.
 for _ in range(8):
  z=C.z+up.z*v+axis.z*d
  target=interp_profile(Pold['back_profile_z_y'],z)
  d=(target-C.y-up.y*v)/axis.y
 return d
def dome_center(v):
 if v<=0:return rear_axis_target(v)
 # A single C1 upper continuation, rather than a short fade band that creates a new hump.
 t=min(1,v/re);a=rear_axis_target(0);d0=(rear_axis_target(.01)-rear_axis_target(-.01))/.02
 d1=-.28
 return (2*t**3-3*t*t+1)*a+(t**3-2*t*t+t)*d0*re+(-2*t**3+3*t*t)*18.5+(t**3-t*t)*d1*re
def dome(x,v):
 denom=max(.000001,1-v*v/(re*re));radial=max(0,1-(x*x+v*v)/(re*re))
 return 18.5+(dome_center(v)-18.5)*radial/denom
def lpt(x,v,d):return C+right*x+up*v+axis*d
chord=[wall[16][0]]+[add(lpt(cutx*(1-2*j/K),cutv,dome(cutx*(1-2*j/K),cutv))) for j in range(1,K)]+[wall[16][-1]]
back_boundary=wall[16]+list(reversed(chord))[1:-1]
# interior radial patch, all points stay inside the clipped circular domain
center2=(0.,15.);outer=[((vs[i]-C).dot(right),(vs[i]-C).dot(up)) for i in back_boundary];prev=back_boundary
for k in range(1,25):
 t=k/25;ring=[]
 for x,v in outer:
  xx=x*(1-t)+center2[0]*t;vv=v*(1-t)+center2[1]*t;ring.append(add(lpt(xx,vv,dome(xx,vv))))
 for j in range(len(ring)):quad(prev[j],prev[(j+1)%len(ring)],ring[(j+1)%len(ring)],ring[j])
 prev=ring
ci=add(lpt(*center2,dome(*center2)))
for j in range(len(prev)):fs.append((prev[j],prev[(j+1)%len(prev)],ci))
# Top neck loop is 128 points, starting left axial midpoint and proceeding through front.
top=[wall[k][-1] for k in range(8,-1,-1)]+minor[1:]+[wall[k][0] for k in range(1,17)]+chord[1:]+[wall[k][-1] for k in range(15,8,-1)]
assert len(top)==128,len(top)
NN=128;ov=[v.co.copy()*1000 for v in old.data.vertices];rows=sum(1 for k in range(len(ov)//NN) if ov[k*NN].z<=135.00001)
# Preserve full original lower mesh and use index64 as loop start.
base=len(vs);vs.extend(v.copy() for v in ov[:rows*NN])
for i in range(rows-1):
 for j in range(NN):a=base+i*NN+j;b=base+i*NN+(j+1)%NN;quad(a,b,b+NN,a+NN)
fs.append(tuple(base+j for j in reversed(range(NN))))
bottomloop=[base+(rows-1)*NN+(j+64)%NN for j in range(NN)]
prev=bottomloop
# Cubic Hermite patch: lower tangent derives from actual v005 rows; top tangent follows face/back surface.
for k in range(1,33):
 t=k/33;ring=[]
 for j in range(NN):
  a=vs[bottomloop[j]];b=vs[top[j]];h=b.z-a.z
  earlier=ov[(rows-2)*NN+(j+64)%NN];t0=(a-earlier)/max(.001,a.z-earlier.z)*h
  q=abs(j-32)/32 if j<=64 else (96-abs(j-96))/32
  # Surface end tangent is in planar face for front half; dome derivative for back half.
  backweight=max(0,math.sin(2*math.pi*(j-64)/128))
  local=b-C;vlocal=local.dot(up);xx=local.dot(right)
  dx=(-cutv/cutx)*(xx/cutx)**7
  backweight=max(0,min(1,local.dot(axis)/18.5))
  eps=.01
  dd=(dome(xx+dx*eps,vlocal+eps)-dome(xx-dx*eps,vlocal-eps))/(2*eps)*backweight
  t1=(up+right*dx+axis*dd)*h
  p=(2*t**3-3*t*t+1)*a+(t**3-2*t*t+t)*t0+(-2*t**3+3*t*t)*b+(t**3-t*t)*t1
  ring.append(add(p))
 for j in range(NN):quad(prev[j],prev[(j+1)%NN],ring[(j+1)%NN],ring[j])
 prev=ring
for j in range(NN):quad(prev[j],prev[(j+1)%NN],top[(j+1)%NN],top[j])
head=make('01 Unified exterior - shared cylinder and neck boundary',vs,fs,mat)
# Restore exact float32 source coordinates for every protected lower vertex.
for i in range(rows*NN):head.data.vertices[base+i].co=old.data.vertices[i].co
for i in front_faces:head.data.polygons[i].use_smooth=False
head['cylinder_axis']=list(axis);head['straight_wall_length_mm']=17.7
head['construction']='Explicit corresponding circular arc rings extruded along axis. Bottom attachment shares neck vertices; no Boolean.'
# Obsolete objects removed only in this new scene.
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

rd=[];err=[]
for j in range(M+1):
 a=head.data.vertices[wall[1][j]].co*1000;b=head.data.vertices[wall[15][j]].co*1000;delta=b-a;rd.append(delta.length);err.append((delta-axis*17.7).length)
protected=[tuple(head.data.vertices[base+i].co) for i in range(rows*NN)]
report={'version':'v010a','construction':'shared mesh boundaries; no Boolean, no overlapping head/neck caps','axis_front_to_back_unit':list(axis),'corresponding_ring_pairs':M+1,'straight_wall_axis_distance_min_max_mm':[min(rd),max(rd)],'maximum_ring_vector_error_mm':max(err),'cylinder_major_arc_degrees':math.degrees(math.pi+2*alpha),'bottom_attachment':'Minor lower sector is shared with the neck; exposed sidewall is cylindrical major arc, front circular disc remains complete','lower_body_preserved':{'vertex_count':len(oldpts),'exact_coordinates':protected==oldpts},'topology':[],'limits':['18.5mm axial wall and lower rear shape are visual estimates; new video is not calibrated','Only local cylindrical head correction, no whole-model acceptance','No calibrated physical dimensions or cross-SKU mold verification']}
for ob in [head,face]:
 bm=bmesh.new();bm.from_mesh(ob.data);report['topology'].append({'name':ob.name,'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-14 for f in bm.faces)});bm.free()
(O/'evidence/geometry-check.json').write_text(json.dumps(report,indent=2))
P['head_root_transition']='Original z<=135mm kept exact; shared boundary neck patch joins cylindrical wall corners, planar lower arc and shallow rear chord'
P.pop('side_segments',None);P.pop('head_root_transition_z_mm',None)
P['cylindrical_major_arc_segments']=192;P['planar_front_minor_arc_segments']=48;P['panel_circle_segments']=256
P['construction_report']=report
P['new_video']='../review/neck-video-feedback/9cb27fd5fdb50f38e74d2d46ac19704e_raw.mp4'
P['viewed_frames']=['contact','f007','f009','f017','f028']
P['local_change']='lower rear cap and upper neck; retain exposed circular wall and all lower vertices'
P['rear_axis_samples']=[[v,rear_axis_target(v),dome(0,v)] for v in [-35,-20,0,20,35]]
(B/'parameters-v010a.json').write_text(json.dumps(P,ensure_ascii=False,indent=2))
scene=bpy.context.scene;scene.render.resolution_x=1000;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=95;scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
cam=scene.camera;cam.data.type='ORTHO';T=Vector((0,.017,.1325))
def camera(angle,target=T,scale=.31,elev=0):
 a=math.radians(angle);cam.location=target+Vector((.7*math.sin(a),-.7*math.cos(a),elev));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
camera(55,Vector((0,.02,.200)),.175,.025)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'shower_black_clay_v010a.blend'))
for name,angle,target,scale,elev in [('strict_side',90,T,.31,0),('head_oblique_back',125,Vector((0,.02,.200)),.175,.025)]:
 camera(angle,target,scale,elev);scene.render.filepath=str(O/'renders'/f'{name}.jpg');bpy.ops.render.render(write_still=True)
print('V010A_COMPLETE',O)
