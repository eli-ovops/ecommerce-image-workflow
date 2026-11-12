"""Reopen final .blend before running. Checks are geometric, not product acceptance."""
import bpy,bmesh,json,csv
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent
parts=[o for o in bpy.data.objects if o.type=='MESH']
result={'blend':bpy.data.filepath,'objects':[],'surface_intersections':[],'bore_checks':[],'blind_checks':[]}
bs={}
for ob in parts:
 bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world);bs[ob.name]=BVHTree.FromBMesh(bm)
 result['objects'].append({'name':ob.name,'dimensions_mm':[round(v*1000,6) for v in ob.dimensions],'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume_mm3':bm.calc_volume(signed=True)*1e9,'inconsistent_winding_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges)})
 bm.free()
for i,a in enumerate(parts):
 for b in parts[i+1:]:
  overlap=bs[a.name].overlap(bs[b.name])
  result['surface_intersections'].append({'a':a.name,'b':b.name,'triangle_pairs':len(overlap)})
panel=bpy.data.objects['Recessed_panel_with_true_through_holes']
rows=list(csv.DictReader((P/'hole-map.csv').open()))
for a in rows:
 if a['kind']=='OCCLUDED_KNOB':continue
 origin=Vector((float(a['x_mm'])*.001,float(a['y_mm'])*.001,.0085));direction=Vector((0,0,-1))
 hit,loc,normal,index=panel.ray_cast(origin,direction,distance=.0042)
 if a['kind']=='HOLE':result['bore_checks'].append({'id':a['id'],'open':not hit})
 else:result['blind_checks'].append({'id':a['id'],'closed':bool(hit),'first_surface_z_mm':round(loc.z*1000,5) if hit else None,'normal_z':round(normal.z,5) if hit else None})
result['materials']=[m.name for m in bpy.data.materials]
result['checks']={'all_96_bores_open':len(result['bore_checks'])==96 and all(a['open'] for a in result['bore_checks']),'all_132_blind_dots_closed':len(result['blind_checks'])==132 and all(a['closed'] for a in result['blind_checks']),'all_parts_manifold':all(a['nonmanifold_edges']==0 for a in result['objects']),'all_parts_positive_volume':all(a['signed_volume_mm3']>0 for a in result['objects']),'all_parts_consistent_winding':all(a['inconsistent_winding_edges']==0 for a in result['objects']),'three_finishes_persisted':all(any(s in m for m in result['materials']) for s in ['Silver','Black','Gunmetal'])}
(P/'reopen-verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result['checks']))
assert all(result['checks'].values())
