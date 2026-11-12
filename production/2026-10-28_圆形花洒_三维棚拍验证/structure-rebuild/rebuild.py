import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector,Matrix
B=Path(__file__).resolve().parent;exec((B/'master.py').read_text());bpy.ops.wm.open_mainfile(filepath=str(B/'sources/baseline.blend'));S=bpy.context.scene
old=bpy.data.objects['01 Continuous calibrated exterior'];oldmesh=old.data.copy();oldref=bpy.data.objects.new('Old local shell ray reference',oldmesh);S.collection.objects.link(oldref);oldref.hide_render=True
# Use existing material definitions and independent controls; discard conflicting surfaces.
mats={i:bpy.data.objects[next(o.name for o in S.objects if o.name.startswith(f'{i:02d} '))].data.materials[0] for i in [1,2,3,4,6,8]}
R0=Matrix.Rotation(math.radians(35),4,'Z')@Matrix.Rotation(math.radians(-90),4,'X');oz=old.location.z
kept=[]
for o in list(S.objects):
 if o.name.startswith(('06 ','07 ','08 ','09 ')):
  o.matrix_world=R0.inverted()@Matrix.Translation((0,0,-oz))@o.matrix_world;kept.append(o)
 elif o!=oldref:bpy.data.objects.remove(o,do_unlink=True)
def mesh(name,vs,fs,mat,smooth=True):
 me=bpy.data.meshes.new(name);me.from_pydata([v*.001 for v in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);S.collection.objects.link(o);me.materials.append(mat)
 for f in me.polygons:f.use_smooth=smooth
 return o
# Stable paired surface grids, singleton top/bottom fans, welded perimeter.
def paired(name,zlo,zhi,rows,cols,width,front,back,mat,xmap=None):
 coords=[];rr=[]
 for j in range(rows+1):
  z=zlo+(zhi-zlo)*j/rows;w=width(z);us=[0] if w<1e-5 else [-1+2*i/cols for i in range(cols+1)];row=[]
  for u in us:
   x=xmap(u,z,w) if xmap else u*w;row.append(len(coords));coords.append((x,z))
  rr.append(row)
 faces=[]
 for a,b in zip(rr,rr[1:]):
  if len(a)==1:
   for i in range(len(b)-1):faces.append((a[0],b[i+1],b[i]))
  elif len(b)==1:
   for i in range(len(a)-1):faces.append((a[i],a[i+1],b[0]))
  else:
   for i in range(len(a)-1):faces.append((a[i],a[i+1],b[i+1],b[i]))
 n=len(coords);vs=[front(x,z) for x,z in coords]+[back(x,z) for x,z in coords];fs=faces+[tuple(v+n for v in reversed(f)) for f in faces]
 perimeter=rr[0]+[r[-1] for r in rr[1:]]+list(reversed(rr[-1][:-1]))+[r[0] for r in reversed(rr[1:-1])]
 # Remove repeated singleton indices.
 per=[]
 for i in perimeter:
  if not per or per[-1]!=i:per.append(i)
 for a,b in zip(per,per[1:]+per[:1]):
  if a!=b:fs.append((a,b,b+n,a+n))
 return mesh(name,vs,fs,mat)
def raydepth(x,z,rear=True):
 s=P(x,z);n=normal(z);origin=(s+n*(200 if rear else -200))*.001;hit,loc,_,_=oldref.ray_cast(origin,-n if rear else n)
 if hit:return (loc*1000-s).dot(n)
 return 23 if rear else 0

# Old edge ray misses are not used: continuous center-envelope + analytic cross-section.
DEPTH=[(float(z),raydepth(0,float(z),True)) for z in range(10,275,5)]
DEPTH.append((ZTOP,22.0))
def depth_center(z):return max(22.0,hermite(DEPTH,z))
def cross(x,z):
 u=min(1,abs(x)/max(.0001,W(z)));g=smooth((z-105)/70);c=depth_center(z)
 q=(1-math.sqrt(max(0,1-u*u)))*(1-g)+u*u*g
 front_edge=(c*.5-.25)*(1-g);back_edge=(c*.5+.25)*(1-g)+22*g
 return front_edge*q,c-(c-back_edge)*q
def sf(x,z):
 m=margin(x,z);a=cross(x,z)[0]*smooth((-m-.35)/3)
 return P(x,z,a+seat_depth(x,z))
def sb(x,z):return P(x,z,cross(x,z)[1])
def adaptive_x(u,z,w):
 a=abs(u);p=min(w*.93,WP(z)+.35);q=min(w*.98,p+.95)
 blend=smooth(WP(z)/8)
 if a<=.75:x=p*a/.75
 elif a<=.90:x=p+(q-p)*(a-.75)/.15
 else:x=q+(w-q)*(a-.90)/.10
 return math.copysign(x*blend+a*w*(1-blend),u)
shell=paired('01 Rebuilt continuous silver exterior and seat',10,ZTOP,960,256,W,sf,sb,mats[1])
# Smooth normals on a freshly ordered mesh, no inherited custom normals / fold collapse.
panel=paired('02 Unified perforated panel',PMIN,PMAX,320,96,WP,lambda x,z:P(x,z,0),lambda x,z:P(x,z,PANEL_THICKNESS),mats[2])
back=paired('10 Shared-surface black cavity floor',210-61.9*U,210+61.9*U,240,96,lambda z:math.sqrt(max(0,61.9**2-((z-210)/U)**2)),lambda x,z:P(x,z,BACKING_DEPTH),lambda x,z:P(x,z,BACKING_DEPTH+.25),mats[4])
positions=json.loads((B/'sources/white-hole-layout.json').read_text())['positions_row_x_v_mm'];holes=[]
for row,x,v in positions:holes.append((x,210+v*U,2.0,'white'))
for r in [56,58.6,61]:
 for i in range(100):
  a=i*math.tau/100;holes.append((r*math.cos(a),210+r*math.sin(a)*U,.62,'peripheral'))
vs=[];fs=[]
for x,z,r,kind in holes:
 c=P(x,z);t=tangent(z);n=normal(z);N=48 if kind=='white' else 20;off=len(vs)
 for d in [-.6,1.7]:
  for j in range(N):a=j*math.tau/N;vs.append(c+X*(r*math.cos(a))+t*(r*math.sin(a))+n*d)
 for j in range(N):k=(j+1)%N;fs.append((off+j,off+k,off+N+k,off+N+j))
 fs.append(tuple(off+j for j in reversed(range(N))));fs.append(tuple(off+N+j for j in range(N)))
cut=mesh('Temporary Boolean opening cutters',vs,fs,mats[4]);mod=panel.modifiers.new('Real aperture subtraction','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.context.view_layer.objects.active=panel;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
# Ring and wall geometry share each aperture local normal/tangent.
WV=[];WF=[];BV=[];BF=[]
def rings(vs,fs,x,z,levels,N):
 c=P(x,z);t=tangent(z);n=normal(z);o=len(vs)
 for r,d in levels:
  for j in range(N):a=j*math.tau/N;vs.append(c+X*(r*math.cos(a))+t*(r*math.sin(a))+n*d)
 for k in range(len(levels)-1):
  for j in range(N):a=o+k*N+j;b=o+k*N+(j+1)%N;fs.append((a,b,b+N,a+N))
for x,z,r,kind in holes:
 if kind=='white':
  rings(WV,WF,x,z,[(1.65,.65),(1.60,.35),(.55,.35),(.50,1.6)],64)
  rings(BV,BF,x,z,[(2.0,0),(1.74,.55),(1.74,1.12)],64)
 else:rings(BV,BF,x,z,[(.62,0),(.45,.45),(.45,1.12)],32)
white=mesh('03 Recessed white rings - 144 preserved coordinates',WV,WF,mats[3]);walls=mesh('04 Black aperture well walls',BV,BF,mats[2])
# Keep red control and white connector; no shell rays reference remains in deliverable.
bpy.data.objects.remove(oldref,do_unlink=True)
S['status']='STRUCTURE_CHECK_PENDING';S['dimensions']='Model values only';S['master_surface']='master.py: F(z), inward normal, panel thickness 1.1, cavity floor 2.5, shell seat 3.5 mm';S['white_ring_count']=len(positions)
S.render.engine='BLENDER_WORKBENCH';S.display.shading.light='STUDIO';S.display.shading.color_type='MATERIAL';S.display.shading.show_shadows=True;S.display.shading.show_cavity=True;S.display.shading.background_type='WORLD';S.world.color=(.8,.8,.8);S.view_settings.view_transform='Standard';S.view_settings.exposure=0
# Explicit review diffuse values, independent of shader values.
for m,c in [(mats[1],(.53,.55,.57,1)),(mats[2],(.035,.04,.045,1)),(mats[3],(.85,.85,.80,1)),(mats[4],(.005,.005,.005,1)),(mats[6],(.55,.01,.02,1))]:m.diffuse_color=c
bpy.ops.object.camera_add(location=(.38,-.7,.20));cam=bpy.context.object;S.camera=cam;T=Vector((0,.015,.137));cam.rotation_euler=(T-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.31;S.render.resolution_x=1200;S.render.resolution_y=1500;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.render.filepath=str(B/'structure-gray-v7.png')
bpy.ops.wm.save_as_mainfile(filepath=str(B/'structure-master.blend'));bpy.ops.render.render(write_still=True)
(B/'parameters.json').write_text(json.dumps({'head_diameter_model_mm':130,'panel_thickness_model_mm':1.1,'cavity_floor_depth_model_mm':2.5,'shell_seat_depth_model_mm':3.5,'white_ring_count':len(positions),'peripheral_approximate_count':300,'back_shape':'Old center rear envelope samples with continuous analytic cross-sections; not measured','actual_model':'UNKNOWN','requested_model':'gpt-6-astra','requested_effort':'medium'},indent=2))
print('STRUCTURE_REBUILD_DONE')
