import bpy, json, math
from pathlib import Path
from mathutils import Vector,Matrix
B=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(B/'圆形花洒_三维棚拍.blend'));S=bpy.context.scene
bpy.data.objects['Studio seamless warm-gray surface'].hide_render=True;S.view_settings.exposure=0;S.render.engine='BLENDER_WORKBENCH';S.display.shading.light='STUDIO';S.display.shading.color_type='SINGLE';S.display.shading.single_color=(.48,.48,.48);S.display.shading.show_shadows=True;S.display.shading.show_cavity=True;S.display.shading.background_type='WORLD';S.world.color=(.8,.8,.8);S.view_settings.view_transform='Standard'
S.render.image_settings.file_format='PNG';S.render.filepath=str(B/'same-camera-clay.png');bpy.ops.render.render(write_still=True)
# Front comparison camera in original model coordinates, no fitting or deformation.
R=Matrix.Rotation(math.radians(-35),4,'Z')@Matrix.Rotation(math.radians(-90),4,'X');offset=bpy.data.objects['01 Continuous calibrated exterior'].location.z
T=R@Vector((0,.015,.137));T.z+=offset
S.camera.location=T+R.to_3x3()@Vector((0,-.7,0));S.camera.rotation_euler=(R.to_quaternion()@Vector((0,1,0)).to_track_quat('-Z','Y')).to_euler();S.camera.data.ortho_scale=.31
S.render.resolution_x=1000;S.render.resolution_y=1400;S.render.filepath=str(B/'front-clay.png');bpy.ops.render.render(write_still=True)
(B/'reopen.json').write_text(json.dumps({'reopen_success':True,'lights':[o.name for o in S.objects if o.type=='LIGHT'],'camera_ortho':True,'ai_pixels':False,'blender':bpy.app.version_string,'product_meshes':len([o for o in S.objects if o.type=='MESH' and o.name!='Studio seamless warm-gray surface']),'dimensions_not_measurements':True,'same_camera_clay':'same-camera-clay.png','front_view':'front-clay.png'},indent=2))
