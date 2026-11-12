import bpy
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'native/static-dry-v2.blend'));sc=bpy.context.scene;c=sc.camera;c.location=(.24,-.04,.6)
z=c.location.normalized();x=Vector((0,1,0)).cross(z).normalized();y=z.cross(x).normalized();c.rotation_euler=Matrix((x,y,z)).transposed().to_euler();c.data.ortho_scale=.40
sc.render.filepath=str(P/'native/static-dry-v3.png');bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/static-dry-v3.blend'));bpy.ops.render.render(write_still=True)
