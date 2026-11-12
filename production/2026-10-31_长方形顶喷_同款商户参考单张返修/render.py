import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'input.blend'))
s=bpy.context.scene;preview='--preview' in sys.argv
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def bsdf(m):return next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
panel=bpy.data.objects['Recessed_panel_with_true_through_holes'];m=panel.data.materials[0].copy();m.name='SKU black micrograin - 372 376 calibrated';panel.data.materials[0]=m
for n in m.node_tree.nodes:
 if n.type=='TEX_NOISE':n.inputs['Scale'].default_value=3800;n.inputs['Detail'].default_value=2.5
 if n.type=='VALTORGB':
  n.color_ramp.elements[0].color=(.012,.014,.017,1);n.color_ramp.elements[1].color=(.024,.027,.031,1)
 if n.type=='MAP_RANGE':n.inputs['To Min'].default_value=.27;n.inputs['To Max'].default_value=.40
 if n.type=='BEVEL':n.inputs['Radius'].default_value=.00028;n.samples=8
 if n.type=='BUMP':n.inputs['Strength'].default_value=.8;n.inputs['Distance'].default_value=.00010
bsdf(m).inputs['Metallic'].default_value=0;bsdf(m).inputs['Specular IOR Level'].default_value=.42
knob=bpy.data.objects['Outward_pull_knob_concave_face'];red=knob.data.materials[0].copy();red.name='SKU red satin - source372';knob.data.materials[0]=red
bsdf(red).inputs['Base Color'].default_value=(.83,.008,.001,1);bsdf(red).inputs['Roughness'].default_value=.24;bsdf(red).inputs['Specular IOR Level'].default_value=.34
# Preserve mirror silver color and metallic identity; refine reflected highlight clarity only.
shell=bpy.data.objects['Housing_300x200x20'];silver=shell.data.materials[0].copy();silver.name='Silver mirror - source374';shell.data.materials[0]=silver;bsdf(silver).inputs['Roughness'].default_value=.10
def plain(name,col,rough=.4,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=bsdf(m);b.inputs['Base Color'].default_value=(*col,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;return m
stone=plain('Original dark stone surface',(.012,.014,.016),.26)
nt=stone.node_tree;tex=nt.nodes.new('ShaderNodeTexCoord');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=5;noise.inputs['Detail'].default_value=4;noise.inputs['Roughness'].default_value=.65;nt.links.new(tex.outputs['Object'],noise.inputs['Vector'])
r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.37;r.color_ramp.elements[0].color=(.007,.009,.012,1);r.color_ramp.elements[1].position=.65;r.color_ramp.elements[1].color=(.025,.028,.032,1);nt.links.new(noise.outputs['Fac'],r.inputs[0]);nt.links.new(r.outputs['Color'],bsdf(stone).inputs['Base Color'])
v=nt.nodes.new('ShaderNodeTexVoronoi');v.feature='DISTANCE_TO_EDGE';v.inputs['Scale'].default_value=11;nt.links.new(noise.outputs['Color'],v.inputs['Vector'])
vein=nt.nodes.new('ShaderNodeValToRGB');vein.color_ramp.elements[0].position=.006;vein.color_ramp.elements[0].color=(.11,.105,.09,1);vein.color_ramp.elements[1].position=.021;vein.color_ramp.elements[1].color=(.012,.014,.017,1);nt.links.new(v.outputs['Distance'],vein.inputs[0])
mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[0].default_value=.035;nt.links.new(r.outputs['Color'],mix.inputs[1]);nt.links.new(vein.outputs['Color'],mix.inputs[2]);nt.links.new(mix.outputs[0],bsdf(stone).inputs['Base Color'])
floor=bpy.data.objects['Seamless stage'];floor.data.materials.clear();floor.data.materials.append(stone)
def box(name,loc,dim,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);return o
wall=plain('Deep brown architectural wall',(.026,.019,.016),.38)
box('Background wall',(0,.32,.16),(2,.025,.35),wall)
gold=plain('Muted champagne inlay',(.32,.21,.10),.25,.75)
for x in [-.24,.24]:box('Vertical wall joint',(x,.306,.16),(.0015,.001,.35),gold)
box('Back counter edge',(0,.30,-.008),(2,.002,.002),gold)
for o in list(bpy.data.objects):
 if o.type=='LIGHT':bpy.data.objects.remove(o,do_unlink=True)
def area(name,loc,energy,size,sy,color=(1,1,1),target=(0,0,0)):
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='RECTANGLE';d.size=size;d.size_y=sy;d.color=color;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;aim(o,target)
area('Grazing neutral window',(-.28,-.08,.20),4,.22,.12)
area('Silver side long strip',(.12,-.30,.12),4,.36,.14)
area('Soft neutral fill',(.30,.12,.38),2,.30,.40)
area('Face soft reflected window',(-.24,.22,.28),3.8,.10,.32)
area('Warm background accent',(-.30,.25,.18),1,.10,.20,(1,.66,.34),(0,.30,.10))
area('Silver right definition',(.32,.03,.16),1,.05,.30)
bg=next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.16,.18,.21,1);bg.inputs['Strength'].default_value=.12
# Keep the exact previous camera, rig transform and authored geometry.
s.view_settings.exposure+=.15
s.cycles.samples=32 if preview else 256;s.cycles.use_denoising=True
s.render.resolution_percentage=50 if preview else 100;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=97
s.render.filepath=str(P/('preview.jpg' if preview else '01_advertising_refined.jpg'))
if not preview:bpy.ops.wm.save_as_mainfile(filepath=str(P/'01_advertising_refined.blend'))
bpy.ops.render.render(write_still=True)
