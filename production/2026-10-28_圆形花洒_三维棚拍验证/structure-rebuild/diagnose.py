import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(B/'sources/baseline.blend'));o=bpy.data.objects['01 Continuous calibrated exterior'];me=o.data;me.calc_loop_triangles();tri=[tuple(me.vertices[i].co.copy()*1000 for i in t.vertices) for t in me.loop_triangles]
rows=[]
for z in range(10,276,5):
 hits=[]
 for t in tri:
  for a,b in [(t[0],t[1]),(t[1],t[2]),(t[2],t[0])]:
   if (a.z-z)*(b.z-z)<0:
    p=a.lerp(b,(z-a.z)/(b.z-a.z));hits.append(p)
 if not hits:continue
 front=o.ray_cast(Vector((0,-1,z*.001)),Vector((0,1,0)));rear=o.ray_cast(Vector((0,1,z*.001)),Vector((0,-1,0)))
 rows.append({'z':z,'half_width':max(abs(p.x) for p in hits),'min_y':min(p.y for p in hits),'max_y':max(p.y for p in hits),'center_front_y':front[1].y*1000 if front[0] else None,'center_back_y':rear[1].y*1000 if rear[0] else None})
bm=bmesh.new();bm.from_mesh(me);folds=[]
for e in bm.edges:
 if len(e.link_faces)==2 and .11<(e.verts[0].co.z+e.verts[1].co.z)/2<.18:
  angle=e.calc_face_angle();
  if angle>.35:folds.append({'angle_deg':math.degrees(angle),'mid_mm':list((e.verts[0].co+e.verts[1].co)*500)})
r={'shell_vertices':len(me.vertices),'shell_polygons':len(me.polygons),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'shoulder_dihedral_over_20deg':len(folds),'largest_dihedrals':sorted(folds,key=lambda x:-x['angle_deg'])[:12],'sections_mm':rows};bm.free();(B/'shell-diagnosis.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
