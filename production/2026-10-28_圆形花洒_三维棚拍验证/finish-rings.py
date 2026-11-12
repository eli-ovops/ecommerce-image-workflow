import bpy,json,math
from pathlib import Path
from mathutils import Matrix
B=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(B/'圆形花洒_三维棚拍.blend'));S=bpy.context.scene
P=B/'sources/white-hole-layout.json';points=json.loads(P.read_text())['positions_row_x_v_mm']
def fy(z):
 if z>=155:return (5+(210-z)*.1)*.001
 t=max(0,min(1,(z-110)/45));return ((2*t**3-3*t*t+1)*7+(t**3-2*t*t+t)*3.6+(-2*t**3+3*t*t)*10.5+(t**3-t*t)*(-4.5))*.001
vs=[];fs=[];N=64
for row,x,v in points:
 z=210+v/math.sqrt(1.01);start=len(vs)
 for r,d in [(1.65,.08),(1.6,.45),(.53,.45),(.48,-.28)]:
  for i in range(N):
   a=math.tau*i/N;zz=z+r*math.sin(a);vs.append(((x+r*math.cos(a))*.001,fy(zz)-d*.001,zz*.001))
 for k in range(3):
  for i in range(N):
   a=start+k*N+i;b=start+k*N+(i+1)%N;fs.append((a,b,b+N,a+N))
o=bpy.data.objects['03 White nozzles - 144 mapped positions'];mat=o.data.materials[0];me=bpy.data.meshes.new('64 segment recessed rings following panel slope');me.from_pydata(vs,[],fs);me.update();o.data=me;me.materials.append(mat)
for p in me.polygons:p.use_smooth=True
# Flat panel face normals avoid interpolation streaks across Boolean aperture boundaries.
for p in bpy.data.objects['02 Continuous black face and selector surround'].data.polygons:p.use_smooth=False
S['ring_fix']='64 segments, every vertex follows face profile to prevent tilted panel clipping'
S.render.filepath=str(B/'studio-approved-candidate.png');bpy.ops.wm.save_as_mainfile(filepath=str(B/'圆形花洒_三维棚拍.blend'));bpy.ops.render.render(write_still=True)
