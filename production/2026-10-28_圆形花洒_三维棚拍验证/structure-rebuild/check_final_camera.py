import bpy,json,math
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parent;exec((B/'master.py').read_text());bpy.ops.wm.open_mainfile(filepath=str(B/'圆形花洒_截面重建.blend'));S=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();M=bpy.data.objects['02 Unified perforated panel'].matrix_world;pos=json.loads((B/'sources/white-hole-layout.json').read_text())['positions_row_x_v_mm'];w=[];per=[]
def cast(p):
 p=M@(p*.001);hit,loc,n,i,o,m=S.ray_cast(deps,S.camera.location,(p-S.camera.location).normalized(),distance=2);return o.name if hit else None
for row,x,v in pos:
 z=210+v*U;c=P(x,z);t=tangent(z);n=normal(z);hits=[cast(c+X*(1.05*math.cos(a))+t*(1.05*math.sin(a))+n*.35) for a in [0,math.pi/2,math.pi,math.pi*1.5]];w.append({'row':row,'x':x,'v':v,'hits':hits})
for r in [56,58.6,61]:
 for i in range(100):
  a=i*math.tau/100;per.append(cast(P(r*math.cos(a),210+r*math.sin(a)*U,2.5)))
r={'reopen_success':True,'white_rings_4_of_4_first_hits':sum(all(h and h.startswith('03 ') for h in a['hits']) for a in w),'white_total':len(w),'peripheral_camera_centers_first_hit_silver':sum(h and h.startswith('01 ') for h in per),'peripheral_total':len(per),'coverage':'Final saved studio camera, 144 x 4 annulus sample points and 300 peripheral center rays; does not prove every surface pixel or all views','white_probes':w,'peripheral_hits':per};(B/'final-camera-check.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print({k:v for k,v in r.items() if k not in ['white_probes','peripheral_hits']})
