import bpy
from pathlib import Path
B=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(B/'圆形花洒_三维棚拍.blend'));S=bpy.context.scene
S.view_settings.exposure=-.8
S['status']='USER_REVIEW_PENDING'
S.render.filepath=str(B/'studio-exposure-corrected.png')
bpy.ops.wm.save_as_mainfile(filepath=str(B/'圆形花洒_三维棚拍.blend'));bpy.ops.render.render(write_still=True)
