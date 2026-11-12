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
bpy.ops.wm.open_mainfile(filepath=str(P/'商品基线_v3.blend'));base=snap()
bpy.ops.wm.open_mainfile(filepath=str(P/'磨砂精修_同一商品场景.blend'));current=snap(base)
changed={n:base[n]['materials']!=current[n]['materials'] for n in base}
result={'same_objects':set(base)==set(current),'same_mesh':all(base[n]['mesh']==current[n]['mesh'] for n in base),'same_world_transforms':all(base[n]['world']==current[n]['world'] for n in base),'same_modifiers':all(base[n]['modifiers']==current[n]['modifiers'] for n in base),'material_changed_by_object':changed,'only_panel_and_knob_material_changed':{n for n,v in changed.items() if v}=={'Recessed_panel_with_true_through_holes','Outward_pull_knob_concave_face'},'scope':'Reopened saved source and scene; does not confirm physical product precision'}
(P/'reopened-scene-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False));assert all(result[k] for k in ['same_objects','same_mesh','same_world_transforms','same_modifiers','only_panel_and_knob_material_changed'])
