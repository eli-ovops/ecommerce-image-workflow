import bpy, math, json
from pathlib import Path
from mathutils import Vector, Matrix
B=Path(__file__).resolve().parent
SRC=B/'sources/source-v1.blend'
bpy.ops.wm.open_mainfile(filepath=str(SRC)); S=bpy.context.scene
product=[o for o in S.objects if o.type=='MESH']
def material(name,color,metal,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.node_tree.nodes.clear();p=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');p.name='Principled BSDF';out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface']);p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
silver=material('Studio silver - optical approximation',(.72,.74,.76),1,.16)
black=material('Fine matte black',(.004,.005,.006),0,.55)
black.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.08
n=black.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=2200;n.inputs['Detail'].default_value=2
b=black.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.12;b.inputs['Distance'].default_value=.000035;black.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);black.node_tree.links.new(b.outputs['Normal'],black.node_tree.nodes.get('Principled BSDF').inputs['Normal'])
white=material('Warm white polymer',(.78,.77,.70),0,.32); red=material('Red actuator polymer',(.43,.005,.018),0,.26);dark=material('Dark cavities',(.001,.001,.001),0,.65)
exec((B/'recess.py').read_text())
for o in product:
 idx=int(o.name[:2]);m=silver if idx in [1,7] else black if idx in [2,5] else white if idx in [3,8,9] else red if idx==6 else dark;o.data.materials.clear();o.data.materials.append(m)
 for p in o.data.polygons:p.use_smooth=True
 if idx in [1,7]:
  mod=o.modifiers.new('Submillimetre edge softening','BEVEL');mod.width=.00022 if idx==1 else .00035;mod.segments=3;mod.limit_method='ANGLE';mod.angle_limit=.48
  norm=o.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL');norm.keep_sharp=True;norm.weight=30
 # Position whole product face upwards, no independent deformation.
 R=Matrix.Rotation(math.radians(-35),4,'Z') @ Matrix.Rotation(math.radians(-90),4,'X')
 o.matrix_world=[REDACTED_EMAIL]_world
bpy.context.view_layer.update()
minz=min(([REDACTED_EMAIL]).z for o in product for v in o.data.vertices)
for o in product:o.location.z+=-minz+.00015
bpy.context.view_layer.update()
# Neutral continuous tabletop and physical contact shadow.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,0));floor=bpy.context.object;floor.name='Studio seamless warm-gray surface';floor.data.materials.append(material('Warm neutral backdrop',(.56,.535,.49),0,.62))
T=Vector((.073,.105,.025));cam=S.camera;cam.data.type='ORTHO';cam.data.ortho_scale=.335;cam.location=T+Vector((.05,-.28,.62));cam.rotation_euler=(T-cam.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,size,sy):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='RECTANGLE';o.data.size=size;o.data.size_y=sy;o.rotation_euler=(T-o.location).to_track_quat('-Z','Y').to_euler()
area('Large left softbox',(-.42,-.12,.4),8,.18,.45)
area('Right strip reflection',(.35,.18,.28),3,.06,.38)
area('Top fill',(-.3,.45,.4),1.5,.24,.28)
S.world.use_nodes=True;S.world.node_tree.nodes.clear();bg=S.world.node_tree.nodes.new('ShaderNodeBackground');wo=S.world.node_tree.nodes.new('ShaderNodeOutputWorld');S.world.node_tree.links.new(bg.outputs[0],wo.inputs['Surface']);bg.inputs[0].default_value=(.34,.36,.40,1);bg.inputs[1].default_value=.3
S.render.engine='CYCLES';S.cycles.samples=64;S.cycles.use_denoising=True;S.render.resolution_x=1600;S.render.resolution_y=1600;S.render.resolution_percentage=100;S.view_settings.view_transform='AgX';S.view_settings.exposure=-1.7;S.render.image_settings.file_format='PNG';S.render.filepath=str(B/'studio-selected.png')
S['source_model']=str(SRC);S['image_origin']='Entire product, light, surface and shadows rendered in Blender; no AI pixels';S['limitations']='Photograph-estimated geometry; simplified peripheral holes and connector; optical materials not measured'
bpy.ops.wm.save_as_mainfile(filepath=str(B/'圆形花洒_三维棚拍.blend'))
bpy.ops.render.render(write_still=True)
