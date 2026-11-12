import bpy,json
from pathlib import Path
B=Path(__file__).resolve().parent;O=B/'v004a/evidence';O.mkdir(exist_ok=True,parents=True)
D={}
for v in ['v003','v004a']:
 bpy.ops.wm.open_mainfile(filepath=str(B/v/f'shower_black_clay_{v}.blend'))
 ob=bpy.data.objects['01 Continuous head-neck-handle shell'];N=128;rows=[]
 for i in range(len(ob.data.vertices)//N):
  vs=[[REDACTED_EMAIL] for p in ob.data.vertices[i*N:(i+1)*N]]
  rows.append({'z':sum(p.z for p in vs)*1000/N,'front':min(p.y for p in vs)*1000,'back':max(p.y for p in vs)*1000,'halfwidth':max(abs(p.x) for p in vs)*1000})
 D[v]={'blend':str(B/v/f'shower_black_clay_{v}.blend'),'rows':rows}
(O/'actual-saved-mesh-profiles.json').write_text(json.dumps(D,indent=2))
print('EXPORTED_ACTUAL_MESH_PROFILES',O)
