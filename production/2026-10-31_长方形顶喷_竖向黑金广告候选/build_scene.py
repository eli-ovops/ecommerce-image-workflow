import bpy,bmesh,math,json,csv,sys,hashlib,struct
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'input.blend'));scene=bpy.context.scene
rig=bpy.data.objects['Product_RIG_RIGID_ONLY'];keep={rig,*rig.children}
for o in list(bpy.data.objects):
 if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
old=bpy.data.objects['Recessed_panel_with_true_through_holes'];face=old.data.materials[0];old.name='OLD_PANEL_TEMP'
recipe=(P/'baseline_recipe.py').read_text()
exec(recipe[recipe.index('def mesh('):recipe.index('def material(')])
exec(recipe[recipe.index('def rr('):recipe.index('# Actual enclosed shell')])
section=recipe[recipe.index("panel=profile_rr("):recipe.index('# lathed editable external parts')]
# Preserve planar petal extents and centers; replace razor-thin annular engraving
# with a full shallow inset, as visible in 372/376/382. Depth is a visual estimate.
section=section.replace('ring_prism(poly,inner,6.82,7.65)','prism(poly,6.92,7.65)')
section=section.replace('bev.width=.00006;bev.segments=2','bev.width=.00016;bev.segments=4')
expected=(P/'hole-map.csv').read_bytes()
exec(section)
assert (P/'hole-map.csv').read_bytes()==expected
panel.parent=rig;panel.matrix_basis=old.matrix_basis.copy();panel.matrix_parent_inverse=old.matrix_parent_inverse.copy();bpy.data.objects.remove(old,do_unlink=True)
def bsdf(m):return next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
m=face.copy();m.name='Source black fine molded grain';panel.data.materials[0]=m
for n in m.node_tree.nodes:
 if n.type=='TEX_NOISE':n.inputs['Scale'].default_value=2600;n.inputs['Detail'].default_value=3
 if n.type=='VALTORGB':n.color_ramp.elements[0].color=(.012,.014,.017,1);n.color_ramp.elements[1].color=(.025,.028,.032,1)
 if n.type=='MAP_RANGE':n.inputs['To Min'].default_value=.31;n.inputs['To Max'].default_value=.46
 if n.type=='BUMP':n.inputs['Strength'].default_value=.8;n.inputs['Distance'].default_value=.00016
 if n.type=='BEVEL':n.inputs['Radius'].default_value=.00016;n.samples=8
bsdf(m).inputs['Metallic'].default_value=0
shell=bpy.data.objects['Housing_300x200x20'];silver=shell.data.materials[0].copy();silver.name='Neutral silver mirror';shell.data.materials[0]=silver;bsdf(silver).inputs['Roughness'].default_value=.09
red=bpy.data.objects['Outward_pull_knob_concave_face'].data.materials[0];bsdf(red).inputs['Base Color'].default_value=(.85,.008,.001,1);bsdf(red).inputs['Roughness'].default_value=.28
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
R=Matrix.Rotation(math.radians(-10),4,'Z')@Matrix.Rotation(math.radians(-8),4,'X')@Matrix.Rotation(math.pi/2,4,'Z')@Matrix.Rotation(-math.pi/2,4,'Y')
rig.matrix_world=R;bpy.context.view_layer.update()
coords=[[REDACTED_EMAIL] for v in shell.data.vertices];rig.location.z=-min(v.z for v in coords)
bpy.context.view_layer.update();coords=[[REDACTED_EMAIL] for v in shell.data.vertices]
back_y=max(v.y for v in coords)
def mat(name,col,rough=.35,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=bsdf(m);b.inputs['Base Color'].default_value=(*col,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;return m
stone=mat('Dark marble architecture',(.015,.014,.012),.29)
nt=stone.node_tree;tex=nt.nodes.new('ShaderNodeTexCoord');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=7;noise.inputs['Detail'].default_value=5;noise.inputs['Roughness'].default_value=.7;nt.links.new(tex.outputs['Object'],noise.inputs['Vector'])
wave=nt.nodes.new('ShaderNodeTexWave');wave.wave_type='BANDS';wave.bands_direction='DIAGONAL';wave.inputs['Scale'].default_value=3;wave.inputs['Distortion'].default_value=9;wave.inputs['Detail'].default_value=5;wave.inputs['Detail Scale'].default_value=2;nt.links.new(tex.outputs['Object'],wave.inputs['Vector'])
r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.91;r.color_ramp.elements[0].color=(.009,.012,.014,1);r.color_ramp.elements[1].position=.985;r.color_ramp.elements[1].color=(.12,.115,.10,1);nt.links.new(wave.outputs['Color'],r.inputs[0]);nt.links.new(r.outputs[0],bsdf(stone).inputs['Base Color'])
def box(name,loc,dim,ma,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma)
 if bevel:b=o.modifiers.new('Architectural edge','BEVEL');b.width=bevel;b.segments=3
 return o
box('Marble counter',(0,-.11,-.035),(.90,.65,.07),stone,.002)
# Stone support pier behind the product, with top rear shell physically touching it.
box('Rear stone support and wall',(0,back_y+.04,.24),(.54,.08,.48),stone,.001)
bronze=mat('Architectural champagne bronze',(.26,.16,.065),.25,.8)
em=mat('Warm built-in strip',(.6,.35,.12),.35);bsdf(em).inputs['Emission Color'].default_value=(1,.55,.20,1);bsdf(em).inputs['Emission Strength'].default_value=4
for x in [-.235,.235]:
 box('Bronze channel',(x,back_y-.0005,.24),(.006,.003,.48),bronze,.0004)
 box('Warm vertical light',(x,back_y-.0022,.24),(.0014,.0008,.48),em)
box('Back horizontal reveal',(0,back_y-.001,.065),(.54,.001,.002),bronze)
box('Receding side wall',(-.36,.18,.24),(.06,.40,.48),stone,.001)
def area(name,loc,power,size,sy,color=(1,1,1),target=(0,0,.15)):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='RECTANGLE';d.size=size;d.size_y=sy;d.color=color;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;aim(o,target)
area('Left sculpting window',(-.27,-.19,.37),6,.16,.32)
area('Neutral silver stripe',(.27,-.18,.20),3,.055,.36)
area('Front soft fill',(0,-.55,.28),1,.25,.35)
area('Warm wall wash',(-.29,-.03,.35),1.2,.08,.25,(1,.63,.30),(-.24,back_y,.22))
bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.18,.20,.23,1);bg.inputs[1].default_value=.15
d=bpy.data.cameras.new('Advertising portrait camera');d.type='PERSP';d.lens=62;d.clip_start=.001
camera=bpy.data.objects.new('Advertising portrait camera',d);scene.collection.objects.link(camera);camera.location=(.26,-.67,.29);aim(camera,(0,0,.155));scene.camera=camera
scene.view_settings.exposure=0;scene.render.resolution_x=1600;scene.render.resolution_y=1600;scene.render.resolution_percentage=100
scene.cycles.samples=192;scene.cycles.use_denoising=True;scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=97
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'advertising.blend'))
scene.render.resolution_percentage=50;scene.cycles.samples=32;scene.render.filepath=str(P/'scene-preview.jpg');bpy.ops.render.render(write_still=True)
# Close-up before the final render; not a separate deliverable.
camera.location=rig.matrix_world@Vector((-.075,.02,.22));aim(camera,rig.matrix_world@Vector((-.075,.02,.007)));camera.data.type='ORTHO';camera.data.ortho_scale=.075
scene.render.filepath=str(P/'panel-close-preview.jpg');bpy.ops.render.render(write_still=True)
print('SCENE_AND_PANEL_PREVIEWS_DONE',flush=True)
