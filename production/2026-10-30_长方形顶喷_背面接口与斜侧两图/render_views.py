import bpy,bmesh,math,json,hashlib,struct,sys
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'输入_已认可磨砂场景.blend'))
s=bpy.context.scene
names=['Housing_300x200x20','Recessed_panel_with_true_through_holes','Outward_pull_knob_concave_face','Rear_connector_visible_envelope_UNCONFIRMED_thread','Observed_white_protective_cap']
def snap():
 d={}
 for n in names:
  o=bpy.data.objects[n];h=hashlib.sha256()
  for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
  for f in o.data.polygons:h.update(struct.pack('<I',len(f.vertices)));h.update(struct.pack('<'+'I'*len(f.vertices),*f.vertices))
  d[n]={'mesh_sha256':h.hexdigest(),'world':[list(r) for r in o.matrix_world],'modifiers':[(m.type,getattr(m,'width',None),getattr(m,'segments',None)) for m in o.modifiers],'hidden_render':o.hide_render}
 return d
base=snap()
# Keep original capped connector meshes as hidden, editable historical geometry.
for n in names[-2:]:bpy.data.objects[n].hide_render=True;bpy.data.objects[n].hide_viewport=False;bpy.data.objects[n].hide_set(True)
silver=bpy.data.objects[names[0]].data.materials[0]
def mat(name,color,metal,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough;return m
black=mat('Connector dark inner ring — visible appearance only',(.008,.01,.012),0,.38)
wiremat=mat('Screen visible metallic appearance — material UNKNOWN',(.45,.47,.48),.85,.25)
new=[]
def mesh(name,verts,faces,ma):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);s.collection.objects.link(o);o.data.materials.append(ma);new.append(o);return o
def lathe(name,profile,ma,N=128):
 verts=[(r*.001*math.cos(i*math.tau/N),r*.001*math.sin(i*math.tau/N),z*.001) for r,z in profile for i in range(N)];faces=[]
 for j in range(len(profile)):
  k=(j+1)%len(profile)
  for i in range(N):a=j*N+i;b=j*N+(i+1)%N;c=k*N+(i+1)%N;d=k*N+i;faces.append((a,b,c,d))
 o=mesh(name,verts,faces,ma)
 for f in o.data.polygons:f.use_smooth=True
 return o
# Estimated exterior preserves original base radius and base attachment z=-10mm.
lathe('Connector_open_metal_envelope_ESTIMATED',[(20.5,-10),(21,-10.8),(21,-12),(19.8,-13),(18.8,-13.5),(18.8,-15),(17,-15.8),(15.4,-16),(15.4,-28.5),(14.8,-30),(14.8,-38.5),(14.4,-39.3),(13.6,-39.7),(12.3,-39.7),(11.5,-39),(11.2,-37.8),(11.2,-30),(0.05,-30),(0.05,-10)],silver)
lathe('Connector_dark_inner_ring_ESTIMATED',[(11.18,-37.8),(10.8,-38.2),(9.7,-38.2),(8.0,-37.4),(7.0,-36.4),(6.8,-35.5),(6.8,-34.5),(11.18,-34.5)],black)
# Crossed wire grid, visual approximation; pitch/count/material are not product specifications.
verts=[];faces=[];rad=.00675;pitch=.00065;wr=.000075
for axis in [0,1]:
 for j in range(-10,11):
  offset=j*pitch;length=math.sqrt(rad*rad-offset*offset);start=len(verts)
  for t in [-length,length]:
   for k in range(8):
    a=k*math.tau/8;cross=offset+wr*math.cos(a);z=-.0353+axis*.00015+wr*math.sin(a)
    verts.append((t,cross,z) if axis==0 else (cross,t,z))
  for k in range(8):faces.append((start+k,start+(k+1)%8,start+8+(k+1)%8,start+8+k))
  faces.extend([tuple(start+k for k in range(7,-1,-1)),tuple(start+8+k for k in range(8))])
grid=mesh('Connector_visible_screen_ESTIMATED_pitch_not_spec',verts,faces,wiremat)
for f in grid.data.polygons:f.use_smooth=len(f.vertices)==4
lathe('Connector_dark_cavity_backing_ESTIMATED',[(.01,-34.8),(7,-34.8),(7,-33.5),(.01,-33.5)],black)
for o in new:
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
rig=bpy.data.objects.new('Product_RIG_RIGID_ONLY',None);s.collection.objects.link(rig)
for o in [bpy.data.objects[n] for n in names]+new:o.parent=rig
for o in new:o['evidence']='sources: two uncapped connector photos';o['precision']='Visual estimate only; thread spec, ring dimensions, screen pitch/material/performance UNKNOWN'
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def camera(name,vector,target,scale):
 d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=scale;d.clip_start=.001;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=Vector(target)+Vector(vector);aim(o,target);return o
back=camera('03_背面去盖接口',(.12,-.20,.52),(0,0,.005),.375)
side=camera('04_正面斜侧20mm',(.20,-.38,.25),(0,0,-.008),.395)
d=bpy.data.lights.new('Back mirror soft reflection','AREA');d.energy=3.5;d.shape='RECTANGLE';d.size=.32;d.size_y=.45
rear_light=bpy.data.objects.new('Back mirror soft reflection',d);s.collection.objects.link(rear_light);rear_light.location=(-.12,.25,.32);aim(rear_light,(0,0,0))
# Narrow reflected strip reinforces the sidewall without altering product thickness.
light=bpy.data.lights['White strip for silver'];light.energy=1.5
s.cycles.samples=128;s.cycles.use_denoising=True;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=97
preview='--preview' in sys.argv;s.render.resolution_percentage=50 if preview else 100
if preview:s.cycles.samples=24
records={}
for label,cam,angle in [('03_背面去盖接口',back,math.pi),('04_正面斜侧20mm',side,0)]:
 rear_light.hide_render=angle==0
 rig.rotation_euler=(angle,0,0);s.camera=cam;bpy.context.view_layer.update()
 now=snap();inv=rig.matrix_world.inverted()
 assert all(now[n]['mesh_sha256']==base[n]['mesh_sha256'] and now[n]['modifiers']==base[n]['modifiers'] for n in names)
 errors={n:max(abs(([REDACTED_EMAIL][n].matrix_world)[i][j]-base[n]['world'][i][j]) for i in range(4) for j in range(4)) for n in names};print('NORMALIZED_TRANSFORM_ERRORS',errors,flush=True);assert max(errors.values())<1e-6
 records[label]={'original_objects':now,'rigid_transform':[list(r) for r in rig.matrix_world],'normalized_transform_equal':True,'camera':[list(r) for r in cam.matrix_world]}
 suffix='_preview' if preview else ''
 if not preview:bpy.ops.wm.save_as_mainfile(filepath=str(P/(label+'.blend')))
 s.render.filepath=str(P/(label+suffix+'.jpg'));bpy.ops.render.render(write_still=True)
(P/('制作核对_preview.json' if preview else '制作核对.json')).write_text(json.dumps({'base':base,'views':records,'original_meshes_unchanged':True,'old_connector_and_cap_hidden':names[-2:],'new_estimated_connector_parts':[o.name for o in new],'product_body_dimensions_mm':[300,200,20],'no_pull_state':True},ensure_ascii=False,indent=2))
print('TWO_VIEWS_DONE',flush=True)
