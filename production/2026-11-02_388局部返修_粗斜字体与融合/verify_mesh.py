import bpy,json,hashlib,struct
from pathlib import Path
P=Path(__file__).resolve().parent;S=P.parent/'2026-11-02_391安装仰视单张实验'
names=['Housing_300x200x20','ONLY_PHOTO_FACE_NO_DUPLICATE_CIRCLES','Outward_pull_knob_concave_face','Rear_connector_visible_envelope_UNCONFIRMED_thread']
def capture():
 out={}
 for name in names:
  o=bpy.data.objects[name];h=hashlib.sha256()
  for v in o.data.vertices:h.update(struct.pack('3d',*v.co))
  for f in o.data.polygons:h.update(str(tuple(f.vertices)).encode())
  out[name]=h.hexdigest()
 return out
bpy.ops.wm.open_mainfile(filepath=str(S/'391-installation.blend'));a=capture()
bpy.ops.wm.open_mainfile(filepath=str(P/'388-inset.blend'));b=capture();assert a==b
(P/'mesh-check.json').write_text(json.dumps({'all4_source_meshes_unchanged':a==b,'fingerprints':b,'scope':'vertices/topology only; pose camera lighting/materials intentionally changed; not visual or real flow acceptance'},indent=2));print('4 source mesh fingerprints unchanged')
