import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parent;exec((B/'master.py').read_text());bpy.ops.wm.open_mainfile(filepath=str(B/'structure-master.blend'));S=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();positions=json.loads((B/'sources/white-hole-layout.json').read_text())['positions_row_x_v_mm'];white=[];per=[];clearances=[]
def first(origin,d):
 hit,loc,n,idx,o,m=S.ray_cast(deps,origin*.001,d,distance=2);return o.name if hit else None
for row,x,v in positions:
 z=210+v*U;n=normal(z);t=tangent(z);c=P(x,z);norm=[];cam=[]
 for a in [0,math.pi/2,math.pi,math.pi*1.5]:
  p=c+X*(1.05*math.cos(a))+t*(1.05*math.sin(a))+n*.35
  norm.append(first(p-n*20,n));cam.append(first(S.camera.location*1000,(p*.001-S.camera.location).normalized()))
 white.append({'row':row,'x_mm':x,'v_mm':v,'normal_four_probes':norm,'camera_four_probes':cam,'center_normal_hit':first(c-n*20,n)})
for r in [56,58.6,61]:
 for i in range(100):
  a=i*math.tau/100;x=r*math.cos(a);z=210+r*math.sin(a)*U;c=P(x,z);n=normal(z);p=P(x,z,2.5);per.append({'radius':r,'index':i,'normal_hit':first(c-n*20,n),'camera_hit':first(S.camera.location*1000,(p*.001-S.camera.location).normalized())})
shell=bpy.data.objects['01 Rebuilt continuous silver exterior and seat'];bm=bmesh.new();bm.from_mesh(shell.data);sharp=[]
for e in bm.edges:
 if len(e.link_faces)==2 and .11<(e.verts[0].co.z+e.verts[1].co.z)/2<.18 and e.calc_face_angle()>3:sharp.append(e.index)
top={'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-16 for f in bm.faces),'shoulder_adjacent_faces_over_172deg':len(sharp)};bm.free()
for row,x,v in positions:
 z=210+v*U;n=normal(z);c=P(x,z);hit,loc,_,_=shell.ray_cast((c-n*10)*.001,n)
 if hit:clearances.append((loc*1000-c).dot(n)-BACKING_DEPTH-.25)
r={'white_ring_count':len(white),'white_normal_all_four_hits_ring':sum(all(n and n.startswith('03 ') for n in w['normal_four_probes']) for w in white),'white_camera_all_four_hits_ring':sum(all(n and n.startswith('03 ') for n in w['camera_four_probes']) for w in white),'white_center_hits_cavity_floor':sum(w['center_normal_hit'] and w['center_normal_hit'].startswith('10 ') for w in white),'peripheral_count':len(per),'peripheral_normal_hits_floor':sum(p['normal_hit'] and p['normal_hit'].startswith('10 ') for p in per),'peripheral_camera_hits_silver':sum(p['camera_hit'] and p['camera_hit'].startswith('01 ') for p in per),'min_sampled_shell_to_floor_back_clearance_mm':min(clearances),'shell_topology':top,'coverage':'144 rings x4 surface points in local normal and current gray-camera directions, center rays, 300 peripheral center rays; not exhaustive global self-intersection or all-view validation','white_probes':white,'peripheral_probes':per}
(B/'structure-check.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ['white_probes','peripheral_probes']},indent=2))
