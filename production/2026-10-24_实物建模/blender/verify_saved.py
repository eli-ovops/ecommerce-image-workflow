import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parent;V='v003';O=B/V
bpy.ops.wm.open_mainfile(filepath=str(O/f'shower_black_clay_{V}.blend'))
report={'version':V,'blender_version':bpy.app.version_string,'readback':'opened saved blend in separate Blender process','objects':[],'metrology':False}
allpts=[]
for ob in bpy.data.collections['PRODUCT | editable exterior candidate'].objects:
 bm=bmesh.new();bm.from_mesh(ob.data)
 pts=[[REDACTED_EMAIL] for v in ob.data.vertices];allpts+=pts
 lo=[min(v[i] for v in pts)*1000 for i in range(3)];hi=[max(v[i] for v in pts)*1000 for i in range(3)]
 report['objects'].append({'name':ob.name,'vertices':len(ob.data.vertices),'polygons':len(ob.data.polygons),'bounds_mm':{'min':lo,'max':hi},'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'note':'open detail surfaces intentional; main shell expected closed'});bm.free()
lo=[min(v[i] for v in allpts)*1000 for i in range(3)];hi=[max(v[i] for v in allpts)*1000 for i in range(3)]
report['combined_bbox_mm']=[hi[i]-lo[i] for i in range(3)]
ob=bpy.data.objects['01 Continuous head-neck-handle shell'];N=128;profiles=[]
for i in range(len(ob.data.vertices)//N):
 f=ob.data.vertices[i*N+96].co;b=ob.data.vertices[i*N+32].co
 profiles.append({'z_mm':float(f.z*1000),'front_y_mm':float(f.y*1000),'back_y_mm':float(b.y*1000),'width_mm':float(ob.data.vertices[i*N].co.x*2000)})
report['profile_stations']=[min(profiles,key=lambda p:abs(p['z_mm']-z)) for z in [9,30,60,90,110,125,140,155,170,200,230,250,260]]
report['profile_adjacent_tangent_changes_90_to_175_deg']={}
for key in ['front_y_mm','back_y_mm']:
 angles=[]
 for a,b in zip(profiles,profiles[1:]):
  if 90<=a['z_mm']<175:angles.append(math.degrees(math.atan2(b[key]-a[key],b['z_mm']-a['z_mm'])))
 report['profile_adjacent_tangent_changes_90_to_175_deg'][key]=max(abs(a-b) for a,b in zip(angles,angles[1:]))
report['limits']=['Single-object loft plus separate details; no calibrated reconstruction','Open button and connector detail surfaces are exterior mock-up, not watertight manufacturing assembly','Nozzle layout omitted; thread pitch unspecified','Dimensions are modeling parameters, not measurements of the real item']
(O/'saved-model-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'readback':'OK','bbox_mm':report['combined_bbox_mm'],'objects':len(report['objects']),'tangent_change':report['profile_adjacent_tangent_changes_90_to_175_deg']}))
