import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parent; ROOT=B.parents[2]
OLD=B/'construction-source-v010a.blend'
P={'version':'silver-20261027-v1','head_diameter_model_mm':130,'head_wall_model_mm':22,'head_center_model_mm':[0,5,210],'head_up_slope':-.10,'lower_y_scale':.90,'lower_bend_reduction_mm':6,'upper_rear_excess_scale':.55,'white_hole_rows':[4,7,10,11,12,13,10,10,10,13,12,11,10,7,4],'white_hole_pitch_mm':8.3,'row_pitch_mm':7.2,'peripheral_rows':3,'peripheral_holes_per_ring':100,'dimensions_status':'Model estimates only, uncalibrated photographs; not engineering measurements','photo_estimate_ranges_mm':{'diameter':[128,135],'overall':[265,280],'wall':[19,24]},'source_blend':str(OLD),'routing':{'rule':'ROUTING-2026-10-27-v7','requested_model':'gpt-6-astra','requested_effort':'medium','actual_model':'UNKNOWN','actual_effort':'UNKNOWN'}}
if (B/'parameters.json').exists():P.update(json.loads((B/'parameters.json').read_text()))
(B/'parameters.json').write_text(json.dumps(P,ensure_ascii=False,indent=2))
bpy.ops.wm.open_mainfile(filepath=str(OLD))
S=bpy.context.scene
shell=bpy.data.objects['01 Unified exterior - shared cylinder and neck boundary']
for ob in list(bpy.data.objects):
 if ob!=shell:bpy.data.objects.remove(ob,do_unlink=True)
shell.name='01 Continuous calibrated exterior'
C0=Vector((0,6.5626111,200)); A0=Vector((0,.99129218,.13168083)); U0=Vector((0,-.13168083,.99129218))
C=Vector(P['head_center_model_mm']);U=Vector((0,P['head_up_slope'],1)).normalized();A=Vector((0,U.z,-U.y))
def smooth(t):return max(0,min(1,t))**2*(3-2*max(0,min(1,t)))
def deform(p):
 x,y,z=p;local=p-C0;v=local.dot(U0);d=local.dot(A0)
 dd=d*P['head_wall_model_mm']/18.5 if d<=18.5 else P['head_wall_model_mm']+(d-18.5)*P['upper_rear_excess_scale']
 hp=C+Vector((x,0,0))+U*v+A*dd
 lp=Vector((x,y*P['lower_y_scale']-P['lower_bend_reduction_mm']*math.sin(math.pi*max(0,min(z,175))/175),z+10*min(1,z/135)))
 return lp.lerp(hp,smooth((z-120)/55))
for v in shell.data.vertices:v.co=deform(v.co*1000)*.001
def face_profile(z):
 if z>=155:return 5+(210-z)*.1
 t=max(0,min(1,(z-110)/45));return (2*t**3-3*t*t+1)*7+(t**3-2*t*t+t)*3.6+(-2*t**3+3*t*t)*10.5+(t**3-t*t)*(-4.5)
# Remove inherited front-disc/neck curvature break under the continuous insert.
for v in shell.data.vertices:
 z=v.co.z*1000
 if 110<=z<=175 and v.co.y*1000<face_profile(z):v.co.y=face_profile(z)*.001
shell.data.update()
def mat(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);return m
clay=mat('Satin gray - geometry review only',(.53,.55,.56));black=mat('Black insert',(.027,.032,.038));white=mat('White nozzle and connector',(.88,.88,.83));red=mat('Red descaling button',(.65,.018,.035));dark=mat('Hole recess',(.004,.005,.007))
shell.data.materials.clear();shell.data.materials.append(clay)
col=shell.users_collection[0]
def mesh(name,vs,fs,material):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(material)
 for f in me.polygons:f.use_smooth=True
 return ob
# Surface follows the actual deformed shell, not a floating circular sticker.
def front(x,z):
 hit,loc,n,idx=shell.ray_cast(Vector((x*.001,-1,z*.001)),Vector((0,1,0)))
 return loc.y*1000 if hit else (C+U*((z-C.z)/U.z)).y

def interp(tab,z):
 for (a,va),(b,vb) in zip(tab,tab[1:]):
  if a<=z<=b:return va+(vb-va)*(z-a)/(b-a)
 return tab[0][1] if z<tab[0][0] else tab[-1][1]
# Circle blends into the real elongated insert enclosing the selector.
# The shell width is sampled by the explicit outline; planar cylinder face retained above shoulder.
widths=[(-100,0),(-98,7),(-94,12),(-88,15),(-80,18),(-72,22),(-65,27),(-58,33),(-50,41),(-42,47),(-35,52.0)]
vs=[];fs=[];rows=220;cols=64
for j in range(rows+1):
 v=-100+162.5*j/rows
 w=(15.9*math.sqrt(max(0,1-((v+82)/18)**2)) if v<-88 else interp(widths,v)) if v<-35 else math.sqrt(max(0,62.5**2-v*v))
 for i in range(cols+1):
  x=w*(2*i/cols-1);z=C.z+U.z*v;y=face_profile(z)-.55
  vs.append((x*.001,y*.001,z*.001))
for j in range(rows):
 for i in range(cols):
  a=j*(cols+1)+i;fs.append((a,a+1,a+cols+2,a+cols+1))
panel=mesh('02 Continuous black face and selector surround',vs,fs,black)
solid=panel.modifiers.new('Insert thickness','SOLIDIFY');solid.thickness=.00035
# Local surface mounted geometry with explicit cavity walls, no texture.
def ring_geometry(vs,fs,x,z,levels,N=24):
 start=len(vs);base=face_profile(z)-.65
 for r,depth in levels:
  for j in range(N):
   a=2*math.pi*j/N;xx=x+r*math.cos(a);zz=z+r*math.sin(a)
   vs.append((xx*.001,(base-depth)*.001,zz*.001))
 for k in range(len(levels)-1):
  for j in range(N):
   a=start+k*N+j;b=start+k*N+(j+1)%N;fs.append((a,b,b+N,a+N))
WV=[];WF=[];DV=[];DF=[];points=[]
for row in range(15):
 n=[4,7,10,11,12,13,12,13,12,13,12,11,10,7,4][row]
 for i in range(n):
  x=(i-(n-1)/2)*P['white_hole_pitch_mm'];v=(7-row)*P['row_pitch_mm']
  if x*x+v*v<12**2:continue
  z=C.z+U.z*v;points.append([row+1,x,v]);ring_geometry(WV,WF,x,z,[(1.65,.08),(1.6,.45),(.53,.45),(.48,-.28)])
  ring_geometry(DV,DF,x,z,[(.50,-.29),(0,-.30)])
mesh('03 White nozzles - 144 mapped positions',WV,WF,white);mesh('04 Nozzle dark recesses',DV,DF,dark)
# Three observed concentric micro-hole rows. Count is a visual approximation, not factory hole census.
PV=[];PF=[]
for r in (56.0,58.6,61.0):
 for i in range(P['peripheral_holes_per_ring']):
  a=2*math.pi*i/P['peripheral_holes_per_ring'];x=r*math.cos(a);z=C.z+U.z*r*math.sin(a)
  ring_geometry(PV,PF,x,z,[(.65,.05),(.62,.20),(.43,.20),(.40,.02),(0,.02)],16)
mesh('05 Peripheral micro hole mouths - simplified 3 x 100',PV,PF,mat('Micro hole rims',(.07,.075,.08)))
# Central red actuator with annular lip and real visible central cavity.
RV=[];RF=[];ring_geometry(RV,RF,0,C.z,[(9.7,.05),(9.7,.8),(8.7,1.3),(6.1,1.5),(5.4,3.5),(3.1,3.5),(2.6,2.8),(2.6,-.5)],96)
mesh('06 Red descaling actuator',RV,RF,red)
# Rounded tapered selector capsule, face follows shell and tilts modestly outwards.
vs=[];fs=[];N=96;zc=C.z-81
for depth,scale in [(0,1),(2.4,1),(3,.94)]:
 for i in range(N):
  a=2*math.pi*i/N;s=math.sin(a);co=math.cos(a)
  zz=zc+13.5*math.copysign(abs(s)**.65,s);xx=(10.5+1.2*s)*math.copysign(abs(co)**.65,co)*scale
  yy=face_profile(zz)-.8-depth-.06*(zz-zc)
  vs.append((xx*.001,yy*.001,zz*.001))
for k in range(2):
 for i in range(N):a=k*N+i;b=k*N+(i+1)%N;fs.append((a,b,b+N,a+N))
fs.append(tuple(range(2*N,3*N)))
mesh('07 Separate silver selector',vs,fs,clay)
# Interface exterior, white with simplified raised thread helix; standard unknown.
basez=9+10*9/135;bv=[v.co.y*1000 for v in shell.data.vertices if v.co.z<.010];cy=(min(bv)+max(bv))/2
bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=.0102,depth=basez*.001,location=(0,cy*.001,basez*.0005));ob=bpy.context.object;ob.name='08 White connector core - standard UNKNOWN';ob.data.materials.append(white)
vs=[];fs=[];turns=4;steps=384
for j in range(steps+1):
 a=turns*2*math.pi*j/steps;z=1+(basez-2)*j/steps
 for i in range(8):
  t=2*math.pi*i/8;r=10.25+.55*math.cos(t);zz=z+.45*math.sin(t)
  vs.append((r*math.cos(a)*.001,(cy+r*math.sin(a))*.001,zz*.001))
for j in range(steps):
 for i in range(8):a=j*8+i;b=j*8+(i+1)%8;fs.append((a,b,b+8,a+8))
mesh('09 Simplified visible thread - not engineering thread',vs,fs,white)
# Workbench reveals contour and surface; no photographic chrome or lighting claim.
S.render.engine='BLENDER_WORKBENCH';S.display.shading.light='STUDIO';S.display.shading.studiolight_rotate_z=.35;S.display.shading.color_type='MATERIAL';S.display.shading.show_shadows=True;S.display.shading.show_cavity=True;S.display.shading.cavity_type='BOTH';S.display.shading.curvature_ridge_factor=1.1;S.display.shading.curvature_valley_factor=.8;S.display.shading.background_type='WORLD';S.world.color=(.8,.8,.8)
S.render.resolution_x=1200;S.render.resolution_y=1500;S.render.resolution_percentage=100;S.render.image_settings.file_format='JPEG';S.render.image_settings.quality=95;S.view_settings.view_transform='Standard'
bpy.ops.object.camera_add();S.camera=bpy.context.object;S.camera.name='Review camera';S.camera.data.type='ORTHO';S.camera.data.ortho_scale=.31;target=Vector((0,.015,.137));S.camera.location=target+Vector((.45,-.7,.1));S.camera.rotation_euler=(target-S.camera.location).to_track_quat('-Z','Y').to_euler()
S['status']='PENDING_USER_SHAPE_CONFIRMATION';S['dimension_status']=P['dimensions_status'];S['white_nozzle_count']=len(points);S['source_photos']='339,340,342-355 silver SKU'
# Topology check of reused continuous exterior only.
bm=bmesh.new();bm.from_mesh(shell.data);check={'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-14 for f in bm.faces)};bm.free()
(B/'white-hole-layout.json').write_text(json.dumps({'source':'348 manually counted staggered 15 rows; coordinates proportional to face','positions_row_x_v_mm':points,'count':len(points),'row_counts':[sum(p[0]==i for p in points) for i in range(1,16)]},indent=2))
(B/'geometry-check.json').write_text(json.dumps({'shell':check,'mesh_objects':len([o for o in bpy.data.objects if o.type=='MESH']),'white_nozzle_count':len(points)},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(B/'圆形红钮花洒_银色形状校准_v1.blend'))
print('BUILD_COMPLETE',len(points),check)
