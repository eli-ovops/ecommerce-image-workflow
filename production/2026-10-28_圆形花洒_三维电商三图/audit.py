import bpy,json,hashlib,struct
from pathlib import Path
B=Path(__file__).resolve().parent
def snap():
 r={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or not o.name[:2].isdigit():continue
  h=hashlib.sha256()
  for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
  for p in o.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
  r[o.name]=(h.hexdigest(),o.matrix_world.copy())
 return r
bpy.ops.wm.open_mainfile(filepath=str(B/'sources/baseline.blend'));base=snap();res={}
for code in ['A','B','C']:
 bpy.ops.wm.open_mainfile(filepath=str(B/(code+'-scene.blend')));now=snap();delta=[now[k][1]@base[k][1].inverted() for k in base];err=max(abs(a[i][j]-delta[0][i][j]) for a in delta for i in range(4) for j in range(4));same=all(base[k][0]==now[k][0] for k in base);assert same and err<1e-5
 res[code]={'reopened':True,'product_mesh_topology_equal':same,'common_rigid_transform_max_matrix_difference':err,'external_images':[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file]}
(B/'saved-model-audit.json').write_text(json.dumps(res,indent=2));print(res)
