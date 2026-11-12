import bpy
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'native/static-dry.blend'));sc=bpy.context.scene
sc.camera.location=(.025,-.24,.65);sc.camera.rotation_euler=(Vector((0,0,0))-sc.camera.location).to_track_quat('-Z','Y').to_euler();sc.camera.data.ortho_scale=.46
sc.render.filepath=str(P/'native/static-dry-v2.png');bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/static-dry-v2.blend'));bpy.ops.render.render(write_still=True)
