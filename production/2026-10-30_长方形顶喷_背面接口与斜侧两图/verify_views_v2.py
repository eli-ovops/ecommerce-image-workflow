import bpy,json,hashlib,struct
from pathlib import Path
P=Path(__file__).resolve().parent

def snap(names=None):
 d={}
 for o in bpy.data.objects:
  if o.type!='MESH' or (names and o.name not in names):continue
  h=hashlib.sha256()
  for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
  for p in o.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
  materials=[]
  for m in o.data.materials:
   if m is None:
    materials.append(None);continue
   nodes=[]
   for n in m.node_tree.nodes:
    inputs=[]
    for i in n.inputs:
     if hasattr(i,'default_value'):
      v=i.default_value
      try:v=list(v) if not isinstance(v,str) else v
      except TypeError:pass
      if isinstance(v,(str,int,float,bool,list)):inputs.append([i.identifier,v])
    nodes.append([n.type,inputs])
   materials.append(nodes)
  d[o.name]={'mesh':h.hexdigest(),'world':[list(r) for r in o.matrix_world],'materials':materials,'modifiers':[(m.type,getattr(m,'width',None),getattr(m,'segments',None)) for m in o.modifiers]}
 return d
bpy.ops.wm.open_mainfile(filepath=str(P/'商品基线_v3.blend'));v3=snap()
bpy.ops.wm.open_mainfile(filepath=str(P/'输入_已认可磨砂场景.blend'));base=snap(v3)
report={'input_original_geometry_matches_v3':all(base[n]['mesh']==v3[n]['mesh'] for n in v3),'views':{}}
newbase=None
for label in ['03_背面去盖接口_v2','04_正面斜侧20mm']:
 bpy.ops.wm.open_mainfile(filepath=str(P/(label+'.blend')));current=snap(base);rig=bpy.data.objects['Product_RIG_RIGID_ONLY'];inv=rig.matrix_world.inverted()
 errors={n:max(abs(([REDACTED_EMAIL][n].matrix_world)[i][j]-base[n]['world'][i][j]) for i in range(4) for j in range(4)) for n in base}
 added={n:snap([n])[n] for n in bpy.data.objects.keys() if n.startswith('Connector_')}
 geometry={n:added[n]['mesh'] for n in added}
 if newbase is None:newbase=geometry
 shell=bpy.data.objects['Housing_300x200x20'];bounds=[(max(v.co[i] for v in shell.data.vertices)-min(v.co[i] for v in shell.data.vertices))*1000 for i in range(3)]
 checks={'same_original_meshes':all(base[n]['mesh']==current[n]['mesh'] for n in base),'same_original_materials':all(base[n]['materials']==current[n]['materials'] for n in base),'same_modifiers':all(base[n]['modifiers']==current[n]['modifiers'] for n in base),'normalized_world_transforms_equal':max(errors.values())<1e-6,'original_connector_cap_hidden':all(bpy.data.objects[n].hide_render for n in ['Rear_connector_visible_envelope_UNCONFIRMED_thread','Observed_white_protective_cap']),'same_new_connector_geometry_between_views':geometry==newbase,'body_300_200_20':all(abs(a-b)<.001 for a,b in zip(bounds,[300,200,20]))}
 report['views'][label]={'checks':checks,'normalized_world_max_error':errors,'shell_local_bounds_mm':bounds,'original_objects':current,'added_connector_mesh_hashes':geometry,'rigid_world_transform':[list(r) for r in rig.matrix_world]}
 assert all(checks.values())
assert report['input_original_geometry_matches_v3']
report['scope']='Original product data remains unchanged. Back view applies one shared rigid 180-degree flip; front view identity. Visible connector is replaced by four new estimated parts; hidden capped source remains editable. No physical precision, function or photoreal acceptance claim.'
(P/'重开场景核验_v2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v['checks'] for k,v in report['views'].items()},ensure_ascii=False))
