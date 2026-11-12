import bpy,json,hashlib,struct
from pathlib import Path
P=Path(__file__).resolve().parent
def meshhash(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
 for f in o.data.polygons:h.update(struct.pack('<I',len(f.vertices)));h.update(struct.pack('<'+'I'*len(f.vertices),*f.vertices))
 return h.hexdigest()
def mats(o):
 result=[]
 for m in o.data.materials:
  if m is None:result.append(None);continue
  nodes=[]
  for n in m.node_tree.nodes:
   inputs=[]
   for i in n.inputs:
    if not hasattr(i,'default_value'):continue
    v=i.default_value
    try:v=list(v) if not isinstance(v,str) else v
    except TypeError:pass
    if isinstance(v,(str,int,float,bool,list)):inputs.append((i.identifier,v))
   nodes.append((n.name,n.type,inputs))
  result.append({'nodes':nodes,'links':[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links]})
 return result
def snap(names):
 return {n:{'mesh':meshhash(bpy.data.objects[n]),'materials':mats(bpy.data.objects[n]),'local':[list(r) for r in bpy.data.objects[n].matrix_local],'basis':[list(r) for r in bpy.data.objects[n].matrix_basis],'parent_inverse':[list(r) for r in bpy.data.objects[n].matrix_parent_inverse],'mods':[(m.type,getattr(m,'width',None),getattr(m,'segments',None)) for m in bpy.data.objects[n].modifiers]} for n in names}
bpy.ops.wm.open_mainfile(filepath=str(P/'商品基线_v3.blend'))
v3={o.name:meshhash(o) for o in bpy.data.objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(P/'input.blend'))
names=[o.name for o in bpy.data.objects['Product_RIG_RIGID_ONLY'].children]
base=snap(names)
assert all(base[n]['mesh']==h for n,h in v3.items())
report={'input_original_five_meshes_equal_v3':True,'product_parts':names,'views':{}}
for label in ['01_warm_front','02_blue_side','03_dark_back']:
 bpy.ops.wm.open_mainfile(filepath=str(P/(label+'.blend')))
 current=snap(names);rig=bpy.data.objects['Product_RIG_RIGID_ONLY'];inv=rig.matrix_world.inverted()
 errors={n:max(abs(([REDACTED_EMAIL][n].matrix_world)[i][j]-base[n]['local'][i][j]) for i in range(4) for j in range(4)) for n in names}
 shell=bpy.data.objects['Housing_300x200x20'];bounds=[1000*(max(v.co[i] for v in shell.data.vertices)-min(v.co[i] for v in shell.data.vertices)) for i in range(3)]
 checks={'same_nine_product_meshes':all(base[n]['mesh']==current[n]['mesh'] for n in names),'same_material_nodes_inputs_links':all(base[n]['materials']==current[n]['materials'] for n in names),'same_authored_basis_parent_inverse_modifiers':all(base[n]['basis']==current[n]['basis'] and base[n]['parent_inverse']==current[n]['parent_inverse'] and base[n]['mods']==current[n]['mods'] for n in names),'normalized_world_equal':max(errors.values())<1e-6,'shell_300_200_20mm':all(abs(a-b)<.001 for a,b in zip(bounds,[300,200,20])),'old_cap_connector_hidden':all(bpy.data.objects[n].hide_render for n in ['Observed_white_protective_cap','Rear_connector_visible_envelope_UNCONFIRMED_thread'])}
 print('CHECKS',checks,'ERRORS',errors,flush=True)
 assert all(checks.values())
 report['views'][label]={'checks':checks,'normalized_world_max_errors':errors,'local_shell_bounds_mm':bounds,'rigid_transform':[list(r) for r in rig.matrix_world],'product_mesh_hashes':{n:current[n]['mesh'] for n in names}}
report['scope']='Source identity and rendering scene geometry checks only; no physical installation fit, real spray, photoreal or customer acceptance claim.'
(P/'reopened-scene-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v['checks'] for k,v in report['views'].items()},ensure_ascii=False))
