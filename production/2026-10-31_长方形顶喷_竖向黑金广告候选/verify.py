import bpy,bmesh,json,csv,hashlib,struct,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent
def h(o):
 d=hashlib.sha256()
 for v in o.data.vertices:d.update(struct.pack('<3f',*v.co))
 for f in o.data.polygons:d.update(struct.pack('<I',len(f.vertices)));d.update(struct.pack('<'+'I'*len(f.vertices),*f.vertices))
 return d.hexdigest()
def bounds(o):return [[min(v.co[i] for v in o.data.vertices),max(v.co[i] for v in o.data.vertices)] for i in range(3)]
def snapshot():
 return {o.name:{'hash':h(o),'bounds':bounds(o),'basis':[list(r) for r in o.matrix_basis],'parent_inverse':[list(r) for r in o.matrix_parent_inverse]} for o in bpy.data.objects['Product_RIG_RIGID_ONLY'].children}
bpy.ops.wm.open_mainfile(filepath=str(P/'input.blend'));old=snapshot()
bpy.ops.wm.open_mainfile(filepath=str(P/'upright-advertising.blend'));new=snapshot();s=bpy.context.scene
pn='Recessed_panel_with_true_through_holes';panel=bpy.data.objects[pn];shell=bpy.data.objects['Housing_300x200x20'];rig=bpy.data.objects['Product_RIG_RIGID_ONLY']
checks={'same_nine_product_parts':set(old)==set(new),'eight_other_meshes_unchanged':all(old[n]['hash']==new[n]['hash'] for n in old if n!=pn),'only_panel_mesh_changed':old[pn]['hash']!=new[pn]['hash'],'all_authored_relative_transforms_same':all(old[n]['basis']==new[n]['basis'] and old[n]['parent_inverse']==new[n]['parent_inverse'] for n in old),'panel_outer_bounds_same':old[pn]['bounds']==new[pn]['bounds'],'shell300x200x20':all(abs((b-a)*1000-target)<.001 for (a,b),target in zip(bounds(shell),[300,200,20]))}
rows=list(csv.DictReader((P/'hole-map.csv').open()));hits=[]
for a in rows:
 if a['kind']=='OCCLUDED_KNOB':continue
 x=float(a['x_mm'])*.001;y=float(a['y_mm'])*.001
 got,loc,normal,idx=panel.ray_cast(Vector((x,y,.0085)),Vector((0,0,-1)),distance=.0042)
 hits.append({'id':a['id'],'kind':a['kind'],'x_mm':a['x_mm'],'y_mm':a['y_mm'],'panel_hit':bool(got)})
checks['all96_original_hole_centers_open']=sum(a['kind']=='HOLE' for a in hits)==96 and all(not a['panel_hit'] for a in hits if a['kind']=='HOLE')
checks['all132_original_blind_centers_closed']=sum(a['kind']=='BLIND_DOT' for a in hits)==132 and all(a['panel_hit'] for a in hits if a['kind']=='BLIND_DOT')
bm=bmesh.new();bm.from_mesh(panel.data);nonmanifold=sum(not e.is_manifold for e in bm.edges);degenerate=sum(f.calc_area()<1e-14 for f in bm.faces);bm.free();checks['panel_manifold']=nonmanifold==0;checks['panel_no_degenerate_faces']=degenerate==0
coords=[[REDACTED_EMAIL] for v in shell.data.vertices];minz=min(v.z for v in coords);maxy=max(v.y for v in coords)
wall=bpy.data.objects['Rear stone support and wall'];wallfront=wall.location.y-wall.dimensions.y/2
checks['bottom_contacts_counter']=abs(minz)<1e-6;checks['upper_shell_contacts_rear_wall']=abs(maxy-wallfront)<.0001
projected=[world_to_camera_view(s,s.camera,v) for v in coords];height=max(v.y for v in projected)-min(v.y for v in projected);checks['product_height_75to85pct']=.75<=height<=.85
report={'checks':checks,'old':old,'new':new,'hole_center_tests':hits,'nonmanifold_edges':nonmanifold,'degenerate_faces':degenerate,'projected_product_height_fraction':height,'contact_m':{'bottom_z':minz,'rear_shell_y':maxy,'support_wall_front_y':wallfront},'scope':'Visual estimated panel recess refinement. Hole list remains photo candidate, not factory truth. Contact is virtual scene geometry, not mechanical installation.'}
(P/'geometry-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(checks));print('HEIGHT',height)
assert all(checks.values()),checks
