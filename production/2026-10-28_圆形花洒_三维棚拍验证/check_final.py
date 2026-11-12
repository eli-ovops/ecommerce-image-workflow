import bpy,json,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;F=B/'圆形花洒_三维棚拍.blend';bpy.ops.wm.open_mainfile(filepath=str(F));S=bpy.context.scene
r={'reopen_success':True,'blend_sha256':hashlib.sha256(F.read_bytes()).hexdigest(),'version':bpy.app.version_string,'engine':S.render.engine,'resolution':[S.render.resolution_x,S.render.resolution_y],'exposure':S.view_settings.exposure,'lights':[o.name for o in S.objects if o.type=='LIGHT'],'external_images':[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file],'mesh_count':len([o for o in S.objects if o.type=='MESH'])};(B/'final-reopen.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
