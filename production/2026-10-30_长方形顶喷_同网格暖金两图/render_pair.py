import bpy, math, json, hashlib, struct
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
BASE=P/'商品基线_v3.blend'
bpy.ops.wm.open_mainfile(filepath=str(BASE))
s=bpy.context.scene
products=[o for o in bpy.data.objects if o.type=='MESH']
def fingerprint():
 out={}
 for o in products:
  h=hashlib.sha256()
  for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
  for f in o.data.polygons:h.update(struct.pack('<I',len(f.vertices)));h.update(struct.pack('<'+'I'*len(f.vertices),*f.vertices))
  out[o.name]={'mesh_sha256':h.hexdigest(),'matrix_world':[list(v) for v in o.matrix_world],'scale':list(o.scale),'dimensions_mm':[round(x*1000,6) for x in o.dimensions],'modifiers':[(m.name,m.type) for m in o.modifiers]}
 return out
base=fingerprint()
for o in list(bpy.data.objects):
 if o not in products:bpy.data.objects.remove(o,do_unlink=True)
def mat(name,col,metal=0,rough=.4):
 m=bpy.data.materials.new(name);m.use_nodes=True
 bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;return m
stone=mat('Set warm ivory stone',(.43,.31,.19),0,.32)
bronze=mat('Set satin champagne metal',(.45,.27,.105),.75,.25)
wall=mat('Set warm neutral wall',(.33,.23,.13),0,.55)
def box(name,loc,dim,ma,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma)
 if bevel:
  b=o.modifiers.new('Soft set edges','BEVEL');b.width=bevel;b.segments=5
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=b.name)
 return o
box('Stone countertop',(0,0,-.09),(3,3,.018),stone,.006)
# Display support has a real clearance recess for the unchanged rear connector.
plinth=box('Display plinth',(0,0,-.0452),(.345,.245,.07),stone,.008)
bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.032,depth=.055,location=(0,0,-.025));c=bpy.context.object
bpy.context.view_layer.objects.active=plinth;m=plinth.modifiers.new('Connector clearance','BOOLEAN');m.operation='DIFFERENCE';m.object=c;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(c,do_unlink=True)
box('Champagne base',(0,0,-.077),(.351,.251,.008),bronze,.004)
box('Background wall',(0,.43,.32),(2,.03,.9),wall,.004)
for x in [-.38,.28]:box('Background trim',(x,.408,.30),(.008,.009,.9),bronze,.002)
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def lamp(name,loc,target,power,size,ratio,color):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='RECTANGLE';d.size=size;d.size_y=size*ratio;d.color=color
 o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;aim(o,target)
lamp('Neutral large window',(-.27,-.16,.35),(0,0,0),1.4,.26,.65,(1,1,1))
lamp('Warm rim',(.21,.23,.25),(0,0,0),1.3,.22,.2,(1,.75,.42))
lamp('White strip for silver',(.35,-.19,.12),(0,0,0),.8,.28,.18,(1,1,1))
lamp('Backdrop golden wash',(-.3,.05,.42),(0,.42,.15),3,.25,.8,(1,.67,.32))
w=s.world;w.use_nodes=True;b=next(n for n in w.node_tree.nodes if n.type=='BACKGROUND');b.inputs[0].default_value=(.30,.25,.20,1);b.inputs[1].default_value=.12
s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=True;s.view_settings.view_transform='AgX';s.view_settings.exposure=0
s.render.resolution_x=1600;s.render.resolution_y=1600;s.render.resolution_percentage=100;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=97
cams=[]
for name,scale,target in [('01_银色完整顶喷',.415,(0,0,-.012)),('02_静态红钮近景_非拉出',.105,(0,0,.008))]:
 d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=scale;d.clip_start=.001
 o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=Vector(target)+Vector((.18,-.32,.50));aim(o,target);cams.append((name,o))
s.camera=cams[0][1]
assert base==fingerprint()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'暖金两图_同一商品场景_v2.blend'))
records={}
for name,camera in cams:
 s.camera=camera;s.render.filepath=str(P/(name+'_v2.jpg'))
 records[name]={'product':fingerprint(),'camera_matrix':[list(v) for v in camera.matrix_world],'ortho_scale':camera.data.ortho_scale}
 assert records[name]['product']==base
 bpy.ops.render.render(write_still=True)
(P/'mesh-and-transform-verification_v2.json').write_text(json.dumps({'base_blend_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'base':base,'renders':records,'same_mesh_and_world_transform':all(r['product']==base for r in records.values()),'product_materials_unchanged':True,'static_knob_only':True},ensure_ascii=False,indent=2))
print('TWO_RENDERS_DONE',flush=True)
