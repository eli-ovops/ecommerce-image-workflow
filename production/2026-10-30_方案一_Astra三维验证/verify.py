import bpy,json,hashlib,struct
from pathlib import Path
p=Path(__file__).resolve().parent
expected=json.loads((p/'geometry-audit.json').read_text())['product_fingerprints']
bpy.ops.wm.open_mainfile(filepath=str(p/'方案一_Astra_可编辑.blend'),use_scripts=False)
actual={o.name:hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in o.data.vertices)+b''.join(struct.pack('<I',i) for f in o.data.polygons for i in f.vertices)+str(tuple(tuple(x) for x in o.matrix_world)).encode()).hexdigest() for o in bpy.context.scene.objects if o.type=='MESH' and o.name[:2].isdigit()}
assert actual==expected
(p/'reopen-verification.json').write_text(json.dumps({'reopened_blend':True,'mesh_topology_transform_fingerprints_match_baseline':actual==expected,'product_object_count':len(actual),'blender_version':bpy.app.version_string},indent=2))
