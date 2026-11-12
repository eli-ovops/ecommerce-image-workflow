import bpy
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'upright-advertising.blend'));s=bpy.context.scene;rig=bpy.data.objects['Product_RIG_RIGID_ONLY'];cam=s.camera
target=rig.matrix_world@Vector((-.075,.02,.007))
cam.location=rig.matrix_world@Vector((-.075,.02,.22));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.075
s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100;s.cycles.samples=64;s.render.filepath=str(P/'panel-detail-final.jpg');bpy.ops.render.render(write_still=True)
