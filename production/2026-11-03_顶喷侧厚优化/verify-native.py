import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
def collect(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));result={}
 for name in ['Housing_300x200x20','ONLY_PHOTO_FACE_NO_DUPLICATE_CIRCLES','Outward_pull_knob_concave_face']:
  o=bpy.data.objects[name]
  state={'vertices':[list(v.co) for v in o.data.vertices],'polygons':[list(p.vertices) for p in o.data.polygons],'uv':[[list(a.uv) for a in u.data] for u in o.data.uv_layers],'world_transform':[list(r) for r in o.matrix_world]}
  result[name]=hashlib.sha256(json.dumps(state).encode()).hexdigest()
 return result
before=collect(P/'native/product-v2.blend');after=collect(P/'lighting-refine/native/product.blend')
assert before==after
(P/'lighting-refine/native-reopen-verification.json').write_text(json.dumps({'source':'native/product-v2.blend','candidate':'lighting-refine/native/product.blend','mesh_uv_world_transform_unchanged':True,'sha256':after},indent=2))
