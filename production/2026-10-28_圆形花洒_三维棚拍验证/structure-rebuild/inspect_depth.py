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
 a=cross(x,z)[0];b=seat_depth(x,z);h=max(.6-abs(a-b),0)/.6
 return P(x,z,max(a,b)+h*h*.15)
def sb(x,z):return P(x,z,cross(x,z)[1])
def adaptive_x(u,z,w):
 a=abs(u);p=min(w*.93,WP(z)+.35);q=min(w*.98,p+.95)
 blend=smooth(WP(z)/8)
 if a<=.75:x=p*a/.75
 elif a<=.90:x=p+(q-p)*(a-.75)/.15
 else:x=q+(w-q)*(a-.90)/.10
 return math.copysign(x*blend+a*w*(1-blend),u)

print('DEPTH',DEPTH)
