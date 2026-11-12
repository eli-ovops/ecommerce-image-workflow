import bpy,bmesh
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(B/'structure-master.blend'));S=bpy.context.scene;cam=S.camera
T=Vector((0,.015,.137));S.render.resolution_x=1000;S.render.resolution_y=1400
for name,d in [('front',(0,-.7,0)),('side',(-.7,0,0))]:
 cam.location=T+Vector(d);cam.rotation_euler=(-Vector(d)).to_track_quat('-Z','Y').to_euler();S.render.filepath=str(B/(name+'-gray.png'));bpy.ops.render.render(write_still=True)
# Actual local section at x=4.15 model mm, retain positive-X half.
for o in list(S.objects):
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=(.00415,0,0),plane_no=(1,0,0),clear_inner=True,clear_outer=False);bm.to_mesh(o.data);bm.free()
T=Vector((.00415,.022,.160));cam.location=T+Vector((-.7,-.04,0));cam.rotation_euler=(T-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.145;S.render.resolution_x=1000;S.render.resolution_y=1400;S.render.filepath=str(B/'section-gray.png');bpy.ops.render.render(write_still=True)
