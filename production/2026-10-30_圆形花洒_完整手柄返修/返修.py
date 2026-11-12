import bpy
from pathlib import Path
p=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(p.parent/'2026-10-30_圆形花洒_三维光影验证/三维光影验证.blend'))
s=bpy.context.scene
ledge=bpy.data.objects.get('Foreground stone ledge')
if ledge: ledge.hide_render=True
s.camera.data.ortho_scale=.38
s.camera.data.shift_y=.04
s.render.resolution_x=1600;s.render.resolution_y=1600;s.render.resolution_percentage=100;s.cycles.samples=64
s.render.image_settings.file_format='PNG';s.render.filepath=str(p/'完整手柄_无字.png')
bpy.ops.wm.save_as_mainfile(filepath=str(p/'完整手柄_场景.blend'))
bpy.ops.render.render(write_still=True)
