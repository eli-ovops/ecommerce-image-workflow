import bpy,bmesh,math,json,csv,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'input.blend'));scene=bpy.context.scene
rig=bpy.data.objects['Product_RIG_RIGID_ONLY'];keep={rig,*rig.children}
for o in list(bpy.data.objects):
 if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
old=bpy.data.objects['Recessed_panel_with_true_through_holes'];face=old.data.materials[0];old.name='Old_panel_temp'
recipe=(P/'baseline_recipe.py').read_text()
exec(recipe[recipe.index('def mesh('):recipe.index('def material(')])
exec(recipe[recipe.index('def rr('):recipe.index('# Actual enclosed shell')])
part=recipe[recipe.index('panel=profile_rr('):recipe.index('# lathed editable external parts')]
part=part.replace('ring_prism(poly,inner,6.82,7.65)','pass # Leaf relief comes only from original-photo normal map, never inferred holes.')
original_map=(P/'hole-map.csv').read_bytes();exec(part);assert original_map==(P/'hole-map.csv').read_bytes()
panel.parent=rig;panel.matrix_basis=old.matrix_basis.copy();panel.matrix_parent_inverse=old.matrix_parent_inverse.copy();bpy.data.objects.remove(old,do_unlink=True)
def bs(m):return next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
ma=bpy.data.materials.new('Photo372 calibrated normal only - no photographic albedo');ma.use_nodes=True;panel.data.materials[0]=ma;nt=ma.node_tree;b=bs(ma);b.inputs['Base Color'].default_value=(.018,.021,.026,1);b.inputs['Roughness'].default_value=.42;b.inputs['Metallic'].default_value=.02
uv=panel.data.uv_layers.new(name='Planar_original372_registration')
for poly in panel.data.polygons:
 for li in poly.loop_indices:
  v=panel.data.vertices[panel.data.loops[li].vertex_index].co;uv.data[li].uv=((v.x+.1474)/.2948,(v.y+.0974)/.1948)
t=nt.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(P/'372_registered_relief.png'));t.image.colorspace_settings.name='Non-Color';t.image.pack();t.interpolation='Linear'
bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.45;bump.inputs['Distance'].default_value=.00025;nt.links.new(t.outputs['Color'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],b.inputs['Normal'])
noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=5200
coord=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(coord.outputs['Object'],noise.inputs['Vector'])
grain=nt.nodes.new('ShaderNodeBump');grain.inputs['Strength'].default_value=.45;grain.inputs['Distance'].default_value=.000065;nt.links.new(noise.outputs['Fac'],grain.inputs['Height']);nt.links.new(grain.outputs['Normal'],bump.inputs['Normal'])
sh=bpy.data.objects['Housing_300x200x20'];silver=sh.data.materials[0].copy();sh.data.materials[0]=silver;bs(silver).inputs['Roughness'].default_value=.10
inside=bpy.data.materials.new('Internal cavity shadow visualization');inside.use_nodes=True;bs(inside).inputs['Base Color'].default_value=(.003,.003,.003,1);bs(inside).inputs['Roughness'].default_value=.9;sh.data.materials.append(inside)
for f in sh.data.polygons:
 if f.normal.z>.5 and all(sh.data.vertices[i].co.z<-.007 for i in f.vertices):f.material_index=len(sh.data.materials)-1
rig.rotation_euler=(0,0,math.radians(68));rig.location=(0,0,0)
def mat(name,col,rough=.4,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs(m).inputs['Base Color'].default_value=(*col,1);bs(m).inputs['Roughness'].default_value=rough;bs(m).inputs['Metallic'].default_value=metal;return m
stone=mat('Black marble advertising set',(.009,.008,.007),.34);nt=stone.node_tree;tex=nt.nodes.new('ShaderNodeTexCoord');wave=nt.nodes.new('ShaderNodeTexWave');wave.bands_direction='DIAGONAL';wave.inputs['Scale'].default_value=12;wave.inputs['Distortion'].default_value=12;wave.inputs['Detail'].default_value=6;nt.links.new(tex.outputs['Object'],wave.inputs['Vector']);r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.996;r.color_ramp.elements[0].color=(.006,.008,.010,1);r.color_ramp.elements[1].position=.999;r.color_ramp.elements[1].color=(.06,.055,.045,1);nt.links.new(wave.outputs[0],r.inputs[0]);nt.links.new(r.outputs[0],bs(stone).inputs['Base Color'])
def box(name,loc,dim,ma):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma);return o
floor=box('Marble stage',(0,0,-.06),(2,2,.10),stone)
bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=.032,depth=.12,location=(0,0,-.025));cut=bpy.context.object;mod=floor.modifiers.new('Concealed connector relief','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.context.view_layer.objects.active=floor;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
gold=mat('Champagne architectural lines',(.42,.25,.09),.22,.85)
for y in [-.20,.22]:box('Inset horizontal brass',(0,y,-.0095),(2,.0015,.001),gold)
for x in [-.20,.22]:box('Inset vertical brass',(x,0,-.0095),(.0015,2,.001),gold)
# Original curved dark architectural border, outside the product envelope.
archmat=mat('Dark architectural arch',(.014,.011,.010),.5)
verts=[];faces=[]
for radius in [.27,.36]:
 for i in range(65):
  a=math.pi*.2+i*math.pi*.75/64;verts.append((-.18+radius*math.cos(a),.05+radius*math.sin(a),.04))
for i in range(64):faces.append((i,i+1,65+i+1,65+i))
me=bpy.data.meshes.new('Arch');me.from_pydata(verts,[],faces);o=bpy.data.objects.new('Curved architectural border',me);scene.collection.objects.link(o);o.data.materials.append(archmat)
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,size,sy,color=(1,1,1)):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='RECTANGLE';d.size=size;d.size_y=sy;d.color=color;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;aim(o,(0,0,0))
area('Neutral grazing key',(-.30,.10,.32),4,.20,.30)
area('Silver long reflection',(.28,-.12,.20),3,.06,.40)
area('Warm background pool',(.24,.35,.20),3,.12,.22,(1,.60,.26))
area('Soft fill',(0,-.38,.40),1,.30,.35)
bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.18,.20,.23,1);bg.inputs[1].default_value=.14
d=bpy.data.cameras.new('399 diagonal portrait');d.type='ORTHO';d.ortho_scale=.56;d.clip_start=.001;cam=bpy.data.objects.new('399 diagonal portrait',d);scene.collection.objects.link(cam);cam.location=(0,-.25,.72);aim(cam,(0,.025,0));scene.camera=cam
scene.view_settings.exposure=-.8;scene.render.resolution_x=900;scene.render.resolution_y=1600;scene.render.resolution_percentage=50;scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=97
bpy.context.view_layer.update()
projection=[]
for a in rows:
 v=world_to_camera_view(scene,cam,rig.matrix_world@Vector((a['x_mm']*.001,a['y_mm']*.001,.0072)));projection.append({'id':a['id'],'kind':a['kind'],'x_px':v.x*450,'y_px':(1-v.y)*800})
(P/'399-projection.json').write_text(json.dumps(projection,indent=2))
scene.render.filepath=str(P/'399-preview.jpg');bpy.ops.wm.save_as_mainfile(filepath=str(P/'399-preview.blend'));bpy.ops.render.render(write_still=True)
cam.location=rig.matrix_world@Vector((-.075,.02,.23));aim(cam,rig.matrix_world@Vector((-.075,.02,.007)));cam.data.ortho_scale=.085;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=80;scene.render.filepath=str(P/'399-detail.jpg');bpy.ops.render.render(write_still=True)
