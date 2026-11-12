from pathlib import Path
B=Path(__file__).parent
s=(B/'build_model-v007.py').read_text(); pre=s[:s.index('# Build full head')].replace('v007','v008')
core=r'''
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
def dome(x,v):return 18.5+7*(1-(x*x+v*v)/(re*re))
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
  local=b-C;vlocal=local.dot(up);dd=-14*vlocal/(re*re)*backweight
  t1=(up+axis*dd)*h
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
'''
# reuse planar panel and button implementation
panel=s[s.index('# Face disc planar'):s.index('# Pre-render geometry evidence')]
post=r'''
rd=[];err=[]
for j in range(M+1):
 a=head.data.vertices[wall[1][j]].co*1000;b=head.data.vertices[wall[15][j]].co*1000;delta=b-a;rd.append(delta.length);err.append((delta-axis*17.7).length)
protected=[tuple(head.data.vertices[base+i].co) for i in range(rows*NN)]
report={'version':'v008','construction':'shared mesh boundaries; no Boolean, no overlapping head/neck caps','axis_front_to_back_unit':list(axis),'corresponding_ring_pairs':M+1,'straight_wall_axis_distance_min_max_mm':[min(rd),max(rd)],'maximum_ring_vector_error_mm':max(err),'cylinder_major_arc_degrees':math.degrees(math.pi+2*alpha),'bottom_attachment':'Minor lower sector is shared with the neck; exposed sidewall is cylindrical major arc, front circular disc remains complete','lower_body_preserved':{'vertex_count':len(oldpts),'exact_coordinates':protected==oldpts},'topology':[],'limits':['18.5mm axial wall and7mm shallow rear depth are visual estimates','Only local cylindrical head correction, no whole-model acceptance','No calibrated physical dimensions or cross-SKU mold verification']}
for ob in [head,face]:
 bm=bmesh.new();bm.from_mesh(ob.data);report['topology'].append({'name':ob.name,'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-14 for f in bm.faces)});bm.free()
(O/'evidence/geometry-check.json').write_text(json.dumps(report,indent=2))
P['head_root_transition']='Original z<=135mm kept exact; shared boundary neck patch joins cylindrical wall corners, planar lower arc and shallow rear chord'
P['construction_report']=report
(B/'parameters-v008.json').write_text(json.dumps(P,ensure_ascii=False,indent=2))
scene=bpy.context.scene;scene.render.resolution_x=1000;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=95;scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
cam=scene.camera;cam.data.type='ORTHO';T=Vector((0,.017,.1325))
def camera(angle,target=T,scale=.31,elev=0):
 a=math.radians(angle);cam.location=target+Vector((.7*math.sin(a),-.7*math.cos(a),elev));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
camera(55,Vector((0,.02,.200)),.175,.025)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'shower_black_clay_v008.blend'))
for name,angle,target,scale,elev in [('strict_side',90,T,.31,0),('head_oblique_front',55,Vector((0,.02,.200)),.175,.025),('head_oblique_back',125,Vector((0,.02,.200)),.175,.025)]:
 camera(angle,target,scale,elev);scene.render.filepath=str(O/'renders'/f'{name}.jpg');bpy.ops.render.render(write_still=True)
print('V008_COMPLETE',O)
'''
(B/'build_model-v008.py').write_text(pre+core+panel+post)
