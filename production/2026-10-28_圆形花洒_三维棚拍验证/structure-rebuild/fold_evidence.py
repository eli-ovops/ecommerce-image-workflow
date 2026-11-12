import bpy,bmesh,json,math
from pathlib import Path
B=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(B/'sources/baseline.blend'));bm=bmesh.new();bm.from_mesh(bpy.data.objects['01 Continuous calibrated exterior'].data)
records=[]
for e in bm.edges:
 if len(e.link_faces)!=2 or not .15<(e.verts[0].co.z+e.verts[1].co.z)/2<.175:continue
 a,b=e.verts[0].co,e.verts[1].co;angle=e.calc_face_angle()
 if angle<3:continue
 c=[f.calc_center_median() for f in e.link_faces];side=[(b.x-a.x)*(p.z-a.z)-(b.z-a.z)*(p.x-a.x) for p in c]
 records.append({'angle_deg':math.degrees(angle),'edge_mm':[list(a*1000),list(b*1000)],'face_vertices_mm':[[list(v.co*1000) for v in f.verts] for f in e.link_faces],'xz_centroid_signed_sides_mm2':[v*1e6 for v in side],'centroids_same_projected_side':side[0]*side[1]>0})
before=len(records);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));after=sum(len(e.link_faces)==2 and .15<(e.verts[0].co.z+e.verts[1].co.z)/2<.175 and e.calc_face_angle()>3 for e in bm.edges);bm.free();(B/'fold-evidence.json').write_text(json.dumps({'near_180_before':before,'near_180_after_recalculating_winding':after,'same_side_count':sum(r['centroids_same_projected_side'] for r in records),'interpretation':'Same-side projected adjacent face centroids with consistent mesh winding support local folded/collapsed overlapping faces; not a complete global self-intersection test.','examples':records[:6]},indent=2))
