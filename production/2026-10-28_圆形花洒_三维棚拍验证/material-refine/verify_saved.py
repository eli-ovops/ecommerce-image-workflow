import bpy,json,hashlib,struct
from pathlib import Path
B=Path(__file__).resolve().parent
source=(B/'refine.py').read_text();a=source.index('def fingerprints():');b=source.index('before=fingerprints()');exec(source[a:b])
bpy.ops.wm.open_mainfile(filepath=str(B/'圆形花洒_材质精修.blend'));S=bpy.context.scene
old=json.loads((B/'geometry-fingerprints.json').read_text());now=fingerprints();# JSON tuples normalize to lists
same=json.loads(json.dumps(now))==old['before'];cam={'matrix':[list(r) for r in S.camera.matrix_world],'ortho_scale':S.camera.data.ortho_scale}
r={'reopen_success':True,'saved_geometry_and_transforms_equal_baseline':same,'saved_camera_equal_baseline':cam==old['camera'],'external_images':[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file]};assert same and r['saved_camera_equal_baseline'];(B/'saved-verification.json').write_text(json.dumps(r,indent=2));print(r)
