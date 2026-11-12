import bpy,sys
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'03_背面去盖接口.blend'))
s=bpy.context.scene;o=bpy.data.objects['Back mirror soft reflection'];o.data.size=.14;o.data.size_y=.40;o.data.energy=1.4
preview='--preview' in sys.argv
s.render.resolution_percentage=50 if preview else 100;s.cycles.samples=24 if preview else 128
s.render.filepath=str(P/('03_背面去盖接口_v2_preview.jpg' if preview else '03_背面去盖接口_v2.jpg'))
if not preview:bpy.ops.wm.save_as_mainfile(filepath=str(P/'03_背面去盖接口_v2.blend'))
bpy.ops.render.render(write_still=True)
