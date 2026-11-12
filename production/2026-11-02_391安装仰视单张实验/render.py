import bpy,math,json,random
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent;S=P.parent/'2026-10-31_顶喷孔位回源可控修复'
bpy.ops.wm.open_mainfile(filepath=str(S/'399-preview.blend'));sc=bpy.context.scene
keepnames=['Housing_300x200x20','Outward_pull_knob_concave_face','Rear_connector_visible_envelope_UNCONFIRMED_thread','Product_RIG_RIGID_ONLY']
for o in list(bpy.data.objects):
 if o.name not in keepnames:bpy.data.objects.remove(o,do_unlink=True)
rig=bpy.data.objects['Product_RIG_RIGID_ONLY'];rig.location=(0,0,.55);rig.rotation_euler=(math.pi,0,math.radians(-12))
def bs(m):return next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
def mat(name,c,metal=0,rough=.35):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=bs(m);b.inputs['Base Color'].default_value=(*c,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough;return m
silver=mat('Silver shell controlled neutral reflections',(.68,.72,.76),1,.15)
for name in ['Housing_300x200x20','Rear_connector_visible_envelope_UNCONFIRMED_thread']:
 o=bpy.data.objects[name];o.data.materials.clear();o.data.materials.append(silver)
 for f in o.data.polygons:f.material_index=0
# SINGLE flat rounded photographic front: no secondary hole/leaf/blind-dot geometry.
verts=[]
for cx,cy,start in [(.1471-.0188,.0971-.0188,0),(-.1471+.0188,.0971-.0188,90),(-.1471+.0188,-.0971+.0188,180),(.1471-.0188,-.0971+.0188,270)]:
 for i in range(32):
  a=math.radians(start+i*90/31);verts.append((cx+.0188*math.cos(a),cy+.0188*math.sin(a),.0089))
me=bpy.data.meshes.new('One photographic front surface no relief');me.from_pydata(verts,[],[tuple(range(len(verts)))]);me.update();o=bpy.data.objects.new('ONLY_PHOTO_FACE_NO_DUPLICATE_CIRCLES',me);sc.collection.objects.link(o);o.parent=rig
uv=me.uv_layers.new(name='Direct full rectified photo mapping')
for poly in me.polygons:
 for li in poly.loop_indices:
  v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=((v.x+.15)/.3,(v.y+.1)/.2)
m=mat('Single372 original photo color no bump no second circles',(.1,.1,.1),0,.63);nt=m.node_tree;t=nt.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(P/'single-photo-face.png'));t.image.pack();mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.22,.22,.22,1);nt.links.new(t.outputs['Color'],mix.inputs[1]);nt.links.new(mix.outputs[0],bs(m).inputs['Base Color']);bs(m).inputs['Specular IOR Level'].default_value=.06;em=nt.nodes.new('ShaderNodeEmission');em.inputs['Strength'].default_value=.8;nt.links.new(t.outputs['Color'],em.inputs['Color']);nt.links.new(em.outputs[0],next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL').inputs['Surface']);o.data.materials.append(m)
# Red native knob appears only once. Original central photographed knob footprint is masked beneath it.
red=mat('Red pull knob',(.7,.015,.002),0,.28);bpy.data.objects['Outward_pull_knob_concave_face'].data.materials[0]=red
pipe=mat('Illustrative chrome connection pipe not included SKU',(.44,.5,.55),1,.17)
def curve(name,pts,r,ma):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=16;cu.bevel_depth=r;cu.bevel_resolution=3;sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
 for b,p in zip(sp.bezier_points,pts):b.co=p;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
 ob=bpy.data.objects.new(name,cu);sc.collection.objects.link(ob);ob.data.materials.append(ma);return ob
path=[]
for i in range(17):
 a=math.pi*.5*i/16;path.append((-.034+.034*math.cos(a),0,.586+.034*math.sin(a)))
path.append((-.25,0,.62))
for i in range(1,17):
 a=math.pi*.5+math.pi*.5*i/16;path.append((-.25+.04*math.cos(a),0,.58+.04*math.sin(a)))
path.append((-.29,0,-.1))
cu=bpy.data.curves.new('Illustrative pipe rounded90degree bends','CURVE');cu.dimensions='3D';cu.bevel_depth=.009;cu.bevel_resolution=4;sp=cu.splines.new('POLY');sp.points.add(len(path)-1)
for pt,xyz in zip(sp.points,path):pt.co=(*xyz,1)
ob=bpy.data.objects.new('Illustrative connected pipe',cu);sc.collection.objects.link(ob);ob.data.materials.append(pipe)
# Physically separate illustrative water strands, only at photo-classified dark-hole positions.
water=mat('Illustrative water IOR1.333',(.78,.9,1),0,.07);bs(water).inputs['Transmission Weight'].default_value=.85;bs(water).inputs['IOR'].default_value=1.333
bpy.context.view_layer.update();points=json.loads((P/'water-origins.json').read_text());random.seed(391);origins=[]
for i,p in enumerate(points):
 start=rig.matrix_world@Vector((p['x'],p['y'],.0091));length=random.uniform(.40,.57);dx=random.uniform(-.009,.009);dy=random.uniform(-.009,.009)
 pts=[start,start+Vector((dx*.05,dy*.05,-.035)),start+Vector((dx*.35,dy*.35,-length*.48)),start+Vector((dx,dy,-length))]
 ob=curve('WATER_'+p['id'],pts,random.uniform(.00023,.00036),water);origins.append(dict(id=p['id'],world=list(start),length=length))
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,target,power,size,color):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);sc.collection.objects.link(o);o.location=loc;aim(o,target)
area('Large neutral front reflection',(.2,-.45,.35),(0,0,.5),12,.6,(.85,.93,1))
area('Warm right rim',(.4,.15,.55),(0,0,.5),18,.35,(1,.7,.42))
area('Cool left overhead',(-.4,-.1,.8),(0,0,.5),15,.45,(.45,.65,1))
area('Water backlight',(.12,.25,.3),(0,0,.3),25,.5,(1,.92,.8))
sc.world.use_nodes=True;bg=next(n for n in sc.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.35,.4,.5,1);bg.inputs[1].default_value=.35
ca=bpy.data.cameras.new('391 installed low angle');ca.type='ORTHO';ca.ortho_scale=.68;ca.clip_start=.001;cam=bpy.data.objects.new('391 installed low angle',ca);sc.collection.objects.link(cam);cam.location=(.32,-.58,.05);aim(cam,(-.015,0,.35));sc.camera=cam
sc.render.engine='CYCLES';sc.cycles.samples=64;sc.cycles.use_denoising=True;sc.render.film_transparent=True;sc.view_settings.view_transform='AgX';sc.view_settings.exposure=-.7;sc.render.resolution_x=1200;sc.render.resolution_y=1200;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA'
bpy.context.view_layer.update();report={'single_photo_face':True,'photo_shader':'Emission0.8 retains baked photographic tones; deliberate nonphysical appearance reference to avoid double relighting','old_panel_removed':'Recessed_panel_with_true_through_holes' not in bpy.data.objects,'visible_circle_geometry_count':0,'excluded_uncertain_ids':['R03C06','R13C06'],'water_origin_count':94,'water_origins':origins,'camera':list(cam.location),'target':[-.015,0,.35],'renderer':'Cycles','samples':64,'illustration_only':True,'no_verified_installation_or_flow':True,'projection':[]}
for p in points:
 v=world_to_camera_view(sc,cam,rig.matrix_world@Vector((p['x'],p['y'],.0091)));report['projection'].append(dict(id=p['id'],x=v.x*1200,y=(1-v.y)*1200))
(P/'render-record.json').write_text(json.dumps(report,indent=2));sc.render.filepath=str(P/'391-render.png');bpy.ops.wm.save_as_mainfile(filepath=str(P/'391-installation.blend'));bpy.ops.render.render(write_still=True)
