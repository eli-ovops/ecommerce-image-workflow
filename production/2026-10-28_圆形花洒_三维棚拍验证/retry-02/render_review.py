import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
B=Path(__file__).resolve().parent;F=B/'圆形花洒_retry02.blend';bpy.ops.wm.open_mainfile(filepath=str(F));S=bpy.context.scene
for o in S.objects:
 if o.type=='MESH' and not o.name[:2].isdigit():o.hide_render=True
S.render.engine='BLENDER_WORKBENCH';S.view_settings.view_transform='Standard';S.view_settings.exposure=0;S.display.shading.light='STUDIO';S.display.shading.color_type='SINGLE';S.display.shading.single_color=(.5,.5,.5);S.display.shading.show_shadows=True;S.display.shading.show_cavity=True;S.display.shading.background_type='WORLD';S.world.color=(.85,.85,.85)
R=Matrix.Rotation(math.radians(35),4,'Z')@Matrix.Rotation(math.radians(-90),4,'X');T=R@Vector((0,.015,.137));T.z+=bpy.data.objects['01 Continuous calibrated exterior'].location.z
S.render.resolution_x=1000;S.render.resolution_y=1400;S.camera.data.ortho_scale=.31;S.render.image_settings.file_format='PNG'
for name,pos in [('front-gray',(0,-.7,0)),('side-gray',(-.7,0,0))]:
 d=Vector(pos);S.camera.location=T+R.to_3x3()@d;S.camera.rotation_euler=(R.to_quaternion()@(-d).to_track_quat('-Z','Y')).to_euler();S.render.filepath=str(B/(name+'.png'));bpy.ops.render.render(write_still=True)
(B/'reopen.json').write_text(json.dumps({'success':True,'blend_sha256':hashlib.sha256(F.read_bytes()).hexdigest(),'blender':bpy.app.version_string,'views_same_saved_model':True,'camera_uncalibrated':True,'dimensions_are_measurements':False,'lights':[o.name for o in S.objects if o.type=='LIGHT'],'external_image_dependencies':[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file]},indent=2))
