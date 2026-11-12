import bpy,math,json,hashlib,struct,sys
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'商品输入_同网格磨砂去盖接口.blend'))
s=bpy.context.scene;rig=bpy.data.objects['Product_RIG_RIGID_ONLY'];products=list(rig.children)
def snapshot():
 out={}
 for o in products:
  h=hashlib.sha256()
  for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
  for f in o.data.polygons:h.update(struct.pack('<I',len(f.vertices)));h.update(struct.pack('<'+'I'*len(f.vertices),*f.vertices))
  out[o.name]={'mesh':h.hexdigest(),'matrix_local':[list(r) for r in o.matrix_local],'materials':[m.name if m else None for m in o.data.materials],'modifiers':[(m.type,getattr(m,'width',None),getattr(m,'segments',None)) for m in o.modifiers]}
 return out
base=snapshot()
for o in list(bpy.data.objects):
 if o!=rig and o not in products:bpy.data.objects.remove(o,do_unlink=True)
rig.rotation_euler=(0,0,0);rig.location=(0,0,0)
def material(name,color,rough=.5,metal=0,grain=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;b=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
 if grain:
  t=nt.nodes.new('ShaderNodeTexCoord');n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=grain;n.inputs['Detail'].default_value=2;nt.links.new(t.outputs['Object'],n.inputs['Vector']);bu=nt.nodes.new('ShaderNodeBump');bu.inputs['Strength'].default_value=.2;bu.inputs['Distance'].default_value=.00015;nt.links.new(n.outputs['Fac'],bu.inputs['Height']);nt.links.new(bu.outputs['Normal'],b.inputs['Normal'])
 return m
stone=material('Bathroom limestone warm white',(.58,.53,.44),.48,grain=260)
plaster=material('Bathroom soft white plaster',(.72,.69,.62),.65,grain=500)
grout=material('Warm gray fine grout',(.31,.29,.25),.75)
cloth=material('Ivory cotton towel',(.72,.68,.57),.95,grain=2400)
amber=material('Unbranded amber bathroom bottle',(.075,.035,.013),.2)
chrome=bpy.data.objects['Housing_300x200x20'].data.materials[0]
setobjs=[]
def box(name,loc,dim,ma,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma)
 if bevel:
  b=o.modifiers.new('Set edge radius','BEVEL');b.width=bevel;b.segments=4;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=b.name)
 setobjs.append(o);return o
def cylinder(name,loc,radius,depth,ma,axis=None):
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=radius,depth=depth,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(ma)
 if axis:o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler()
 b=o.modifiers.new('Set soft edge','BEVEL');b.width=.001;b.segments=3
 for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
 setobjs.append(o);return o
def curve(name,coords,radius,ma):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.bevel_depth=radius;d.bevel_resolution=5;sp=d.splines.new('POLY');sp.points.add(len(coords)-1)
 for v,co in zip(sp.points,coords):v.co=(*co,1)
 o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.data.materials.append(ma);setobjs.append(o);return o
wall=box('Limestone tiled shower wall',(0,.40,1.5),(2.4,.08,3),stone)
cut=box('Niche cutter',(-.35,.40,1.73),(.32,.25,.44),stone,.006);bpy.context.view_layer.objects.active=wall;m=wall.modifiers.new('Recessed shelf opening','BOOLEAN');m.operation='DIFFERENCE';m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
box('Niche back',(-.35,.51,1.73),(.32,.02,.44),stone)
box('Niche bottom shelf',(-.35,.43,1.505),(.34,.16,.018),stone,.003)
for x in [-.9,-.6,0,.6,.9]:box('Vertical narrow grout',(x,.359,1.5),(.0015,.002,3),grout)
for z in [.3,.9,1.5,2.1,2.7]:box('Horizontal narrow grout',(0,.359,z),(2.4,.002,.0015),grout)
box('Left plaster return',(-1.1,-.3,1.5),(.05,1.4,3),plaster)
box('Shower ceiling',(0,0,2.85),(2.3,2,.05),plaster)
box('Stone floor',(0,-.4,-.02),(2.3,2,.04),stone)
bench=box('Built in bathroom bench',(0,.16,.80),(1.8,.40,.10),stone,.006)
# Recessed shelf bottles: plain props, no brand or efficacy claims.
for x,h,r in [(-.42,.17,.028),(-.32,.135,.026)]:
 cylinder('Unbranded shelf bottle',(x,.44,1.515+h/2),r,h,amber);cylinder('Bottle plain cap',(x,.44,1.52+h),r*.55,.018,chrome)
# Bathroom context at counter height, with folded towels and an unbranded bottle.
for i in range(3):box('Folded cotton towel '+str(i),(-.37,.16,.86+i*.021),(.25,.16,.019),cloth,.008)
cylinder('Counter soap bottle',(.35,.23,.93),.033,.16,amber);cylinder('Counter pump collar',(.35,.23,1.02),.014,.024,chrome)
curve('Counter pump spout',[(.35,.23,1.04),(.35,.19,1.04)],.004,chrome)
# Plain glass shower screen, edge and clamps provide real room scale.
glass=material('Clear shower glass',(.9,.96,.95),.03);b=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED');b.inputs['Transmission Weight'].default_value=1;b.inputs['IOR'].default_value=1.45
box('Shower screen glass',(.68,-.02,1.15),(.008,.70,2.3),glass,.001)
for z in [.35,1.85]:box('Glass wall clamp',(.68,.33,z),(.028,.035,.04),chrome,.003)
# Installation rod is a generic set fixture, not a product accessory specification.
coords=[(0,.36,2.25),(0,.04,2.25)]
for i in range(1,13):
 a=i*math.pi/2/12;coords.append((0,.04-.04*math.sin(a),2.21+.04*math.cos(a)))
coords.append((0,0,2.1878))
arm=curve('SET_ONLY generic shower arm',coords,.008,chrome)
flange=cylinder('SET_ONLY wall flange',(0,.352,2.25),.025,.012,chrome,(0,1,0))
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def light(name,loc,target,energy,size,size_y,color):
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='RECTANGLE';d.size=size;d.size_y=size_y;d.color=color;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;aim(o,target);return o
light('Broad window daylight',(-.85,-.35,2.1),(0,.1,1.8),35,1.0,1.5,(1,.94,.84))
light('Soft underside reflected fill',(.18,-.70,1.45),(0,0,2.15),6,.65,.75,(1,1,1))
light('Vertical bathroom reflection',(.55,-.10,1.8),(0,0,1.6),12,.18,1.1,(1,1,1))
light('Counter window',(-.5,-.35,1.35),(0,.25,.95),10,.55,.8,(1,.95,.86))
bg=next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.55,.60,.68,1);bg.inputs[1].default_value=.12
# Visible window mullion shadows, kept outside camera foreground.
for z in [1.4,1.95,2.5]:box('Window off-camera horizontal mullion',(-.62,-.25,z),(.035,.06,.024),plaster)
def cam(name,loc,target,lens,aperture):
 d=bpy.data.cameras.new(name);d.type='PERSP';d.lens=lens;d.clip_start=.005;d.dof.use_dof=True;d.dof.focus_distance=(Vector(target)-Vector(loc)).length;d.dof.aperture_fstop=aperture;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;aim(o,target);return o
c1=cam('05_浴室安装全貌',(.37,-.72,1.67),(0,.01,2.12),62,8)
c2=cam('06_安装喷面与红钮',(.16,-.27,1.88),(.04,-.025,2.143),62,11)
c3=cam('07_浴室台面背部接口',(.30,-.38,1.18),(0,.29,.97),62,8)
s.render.engine='CYCLES';s.cycles.samples=128;s.cycles.use_denoising=True;s.render.resolution_x=1600;s.render.resolution_y=1600;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=97;s.view_settings.view_transform='AgX';s.view_settings.exposure=0
preview='--preview' in sys.argv;s.render.resolution_percentage=50 if preview else 100
if preview:s.cycles.samples=24
records={}
for label,camobj,angle in [('05_浴室安装全貌',c1,math.pi),('06_安装喷面与红钮',c2,math.pi),('07_浴室台面背部接口',c3,-2*math.pi/3)]:
 rig.rotation_euler=(angle,0,0)
 if label.startswith('07'):
  R=Matrix.Rotation(angle,3,'X');vs=[[REDACTED_EMAIL] for v in bpy.data.objects['Housing_300x200x20'].data.vertices];rig.location=(0,.36-max(v.y for v in vs),.851-min(v.z for v in vs));arm.hide_render=True;flange.hide_render=True
 else:rig.location=(0,0,2.15);arm.hide_render=False;flange.hide_render=False
 s.camera=camobj;bpy.context.view_layer.update();assert snapshot()==base
 records[label]={'product':snapshot(),'rigid_world':[list(r) for r in rig.matrix_world],'camera':[list(r) for r in camobj.matrix_world],'product_source':'商品输入_同网格磨砂去盖接口.blend','method':'Direct Blender product rendering; no AI product pixels; only shared rigid positioning'}
 suffix='_preview_v2' if preview else '';s.render.filepath=str(P/(label+suffix+'.jpg'))
 if not preview:bpy.ops.wm.save_as_mainfile(filepath=str(P/(label+'.blend')))
 bpy.ops.render.render(write_still=True)
(P/('geometry-preview.json' if preview else 'geometry-production.json')).write_text(json.dumps({'base':base,'views':records,'same_product_mesh_material_slots_local_transforms_modifiers':True},ensure_ascii=False,indent=2));print('THREE_BATHROOM_VIEWS_DONE',flush=True)
