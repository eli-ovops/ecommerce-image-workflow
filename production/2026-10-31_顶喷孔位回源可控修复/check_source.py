import bpy,bmesh,csv,json,math,hashlib,struct
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'399-preview.blend'))
p=bpy.data.objects['Recessed_panel_with_true_through_holes'];shell=bpy.data.objects['Housing_300x200x20']
rows=list(csv.DictReader((P/'hole-map.csv').open()));tests=[]
for a in rows:
 if a['kind']=='OCCLUDED_KNOB':continue
 got,loc,n,idx=p.ray_cast(Vector((float(a['x_mm'])*.001,float(a['y_mm'])*.001,.0085)),Vector((0,0,-1)),distance=.0042)
 tests.append({'id':a['id'],'kind':a['kind'],'hit_panel':bool(got)})
leaves={}
for a in rows:
 for sx in [-1,1]:
  for sy in [-1,1]:
   x=float(a['x_mm'])+sx*5.05;y=float(a['y_mm'])+sy*5.05
   if abs(x)<=138 and abs(y)<=88:leaves[(round(x,3),round(y,3))]=(x,y)
leafhits=[]
for x,y in leaves.values():
 got,*_=p.ray_cast(Vector((x*.001,y*.001,.0085)),Vector((0,0,-1)),distance=.0042);leafhits.append(bool(got))
bm=bmesh.new();bm.from_mesh(p.data);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
dims=[(max(v.co[i] for v in shell.data.vertices)-min(v.co[i] for v in shell.data.vertices))*1000 for i in range(3)]
checks={'96_original_candidate_holes_open':len([a for a in tests if a['kind']=='HOLE'])==96 and all(not a['hit_panel'] for a in tests if a['kind']=='HOLE'),'132_original_blind_circles_closed':len([a for a in tests if a['kind']=='BLIND_DOT'])==132 and all(a['hit_panel'] for a in tests if a['kind']=='BLIND_DOT'),'all_sampled_leaf_centers_closed':all(leafhits),'panel_manifold':nonmanifold==0,'shell300x200x20':all(abs(a-b)<.001 for a,b in zip(dims,[300,200,20]))}
report={'checks':checks,'circle_tests':tests,'leaf_center_samples':len(leafhits),'dimensions_mm':dims,'limits':'Photo candidate classification and regularized positions; not factory truth or photogrammetry. Leaf center ray test plus deterministic cutter recipe, not an image-semantic guarantee. Normal texture cannot create through holes, but apparent false holes still require visual review.'}
(P/'source-check.json').write_text(json.dumps(report,indent=2));print(checks)
assert all(checks.values())
