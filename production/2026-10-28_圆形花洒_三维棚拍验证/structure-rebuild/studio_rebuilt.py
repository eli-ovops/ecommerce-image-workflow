import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
B=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(B/'structure-master.blend'));S=bpy.context.scene
product=[o for o in S.objects if o.type=='MESH' and o.name[:2].isdigit()]
key=bpy.data.objects['07 Separate silver selector'];silver=key.data.materials[0]
def fy(z):
 if z>=155:return (5+(210-z)*.1)*.001
 t=max(0,min(1,(z-110)/45));return ((2*t**3-3*t*t+1)*7+(t**3-2*t*t+t)*3.6+(-2*t**3+3*t*t)*10.5+(t**3-t*t)*(-4.5))*.001
R=Matrix.Rotation(math.radians(35),4,'Z')@Matrix.Rotation(math.radians(-90),4,'X')
for o in product:o.matrix_world=[REDACTED_EMAIL]_world
bpy.context.view_layer.update();minz=min(([REDACTED_EMAIL]).z for o in product for v in o.data.vertices)
for o in product:o.location.z-=minz-.00015
bpy.context.view_layer.update()
# Neutral environment, no imported photography or HDRI.
def mat(name,c,rough=0.5,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.node_tree.nodes.clear();p=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');p.name='BSDF';p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(p.outputs[0],out.inputs['Surface']);return m
bpy.ops.mesh.primitive_plane_add(size=200);floor=bpy.context.object;floor.name='Neutral seamless studio';floor.data.materials.append(mat('Neutral white ground',(.82,.82,.82),.7))
T=Vector((-.075,.105,.025));cam=S.camera;cam.data.type='ORTHO';cam.data.ortho_scale=.35;cam.location=T+Vector((.04,-.27,.62));cam.rotation_euler=(T-cam.location).to_track_quat('-Z','Y').to_euler()
S.world.node_tree.nodes.clear();bg=S.world.node_tree.nodes.new('ShaderNodeBackground');bg.inputs[0].default_value=(.7,.7,.7,1);bg.inputs[1].default_value=.6;wo=S.world.node_tree.nodes.new('ShaderNodeOutputWorld');S.world.node_tree.links.new(bg.outputs[0],wo.inputs[0])
def area(name,loc,power,sz,sy):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='RECTANGLE';o.data.size=sz;o.data.size_y=sy;o.rotation_euler=(T-o.location).to_track_quat('-Z','Y').to_euler()
area('Large neutral key',(-.34,-.10,.48),10,.35,.48);area('Narrow side strip',(.24,.1,.28),3,.045,.32)
# Physical reflection card placed along reflected camera ray at the key.
K=key.matrix_world@Vector((0,fy(129)-.0044,.129));n=(R.to_3x3()@Vector((0,-1,-.06))).normalized();v=(cam.location-K).normalized();refl=(2*n.dot(v)*n-v).normalized()
def card(name,center,size,sy,material):
 bpy.ops.mesh.primitive_plane_add(size=1,location=center);o=bpy.context.object;o.name=name;o.rotation_euler=(K-o.location).to_track_quat('Z','Y').to_euler();o.scale=(size,sy,1);o.data.materials.append(material);o.visible_camera=False;return o
m=bpy.data.materials.new('Soft reflection card with luminance gradient');m.use_nodes=True;m.node_tree.nodes.clear();e=m.node_tree.nodes.new('ShaderNodeEmission');tc=m.node_tree.nodes.new('ShaderNodeTexCoord');sep=m.node_tree.nodes.new('ShaderNodeSeparateXYZ');r=m.node_tree.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.15;r.color_ramp.elements[0].color=(.35,.35,.35,1);r.color_ramp.elements[1].position=.85;r.color_ramp.elements[1].color=(1.6,1.6,1.6,1);out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(tc.outputs['Generated'],sep.inputs[0]);m.node_tree.links.new(sep.outputs['X'],r.inputs[0]);m.node_tree.links.new(r.outputs[0],e.inputs['Color']);m.node_tree.links.new(e.outputs[0],out.inputs[0]);card('Broad white reflection card',K+refl*.38,.30,.38,m)
# Slim black flag gives chrome a dark edge, while most reflection remains bright.
card('Slim dark reflection flag',K+refl*.39+Vector((.18,0,0)),.025,.38,mat('Black flag',(.008,.008,.008),.6))
S.render.engine='CYCLES';S.cycles.samples=96;S.cycles.use_denoising=True;S.render.resolution_x=1600;S.render.resolution_y=1600;S.render.resolution_percentage=100;S.view_settings.view_transform='AgX';S.view_settings.exposure=0
S['status']='STRUCTURE_REBUILD_REVIEW_PENDING';S['method']='Entire Blender image; physical reflection cards; no AI or cutouts';S.render.image_settings.file_format='PNG';S.render.filepath=str(B/'studio-structure.png')
(B/'scene-settings.json').write_text(json.dumps({'key_reflection_point':list(K),'reflection_card_direction':list(refl),'exposure':0,'camera':list(cam.location),'product_rigid_z_degrees':35,'selector_crown_model_mm':.6,'actual_model':'UNKNOWN','requested_model':'gpt-6-astra','requested_effort':'medium'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(B/'圆形花洒_截面重建.blend'));bpy.ops.render.render(write_still=True)
