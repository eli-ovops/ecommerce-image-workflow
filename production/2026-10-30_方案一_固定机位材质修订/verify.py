import bpy,json,hashlib,struct
from pathlib import Path
p=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(p/'固定机位材质修订.blend'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name[:2].isdigit()]
f={o.name:hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in o.data.vertices)+b''.join(struct.pack('<I',i) for face in o.data.polygons for i in face.vertices)+str(tuple(tuple(x) for x in o.matrix_world)).encode()).hexdigest() for o in obs}
a=json.loads((p/'geometry-audit.json').read_text());assert f==a['product_fingerprints']
c=bpy.context.scene.camera
cam={'matrix':list(map(list,c.matrix_world)),'type':c.data.type,'scale':c.data.ortho_scale,'shift':[c.data.shift_x,c.data.shift_y],'lens':c.data.lens}
assert cam==a['camera']
(p/'reopen-verification.json').write_text(json.dumps({'reopen':'PASS','camera_unchanged':'PASS','product_mesh_topology_world_transform':'PASS','objects':len(obs),'fingerprints':f,'precision_scan':False},ensure_ascii=False,indent=2))
