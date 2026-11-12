import bpy,math
from mathutils import Vector
from pathlib import Path
B=Path(__file__).resolve().parent;O=B/'v003'
bpy.ops.wm.open_mainfile(filepath=str(O/'shower_black_clay_v003.blend'))
s=bpy.context.scene;cam=s.camera;target=Vector((0,-.008,.1325))
s.render.resolution_x=720;s.render.resolution_y=900;s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=94
for i in range(72):
 a=math.radians(i*5);cam.location=target+Vector((.7*math.sin(a),-.7*math.cos(a),.025));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
 s.render.filepath=str(O/'turntable_frames'/f'{i:03d}.jpg');bpy.ops.render.render(write_still=True)
print('72_FRAMES_RENDERED_FROM_SAVED_V003')
