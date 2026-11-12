import bpy,math,sys,json,hashlib,struct
from pathlib import Path
from mathutils import Matrix,Vector
B=Path(__file__).resolve().parent;final='final' in sys.argv
bpy.ops.wm.open_mainfile(filepath=str(B/'sources/baseline.blend'));S=bpy.context.scene;cam=S.camera
product=[o for o in S.objects if o.type=='MESH' and o.name[:2].isdigit()]
def fingerprint():return {o.name:hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in o.data.vertices)).hexdigest() for o in product}
before=fingerprint()
for o in list(S.objects):
 if o not in product and o!=cam:bpy.data.objects.remove(o,do_unlink=True)
def material(name,col,rough=.5,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
stone=material('Warm limestone set - not product material',(.64,.57,.47),.62)
nt=stone.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');tc=nt.nodes.new('ShaderNodeNewGeometry');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=160;noise.inputs['Detail'].default_value=3;nt.links.new(tc.outputs['Position'],noise.inputs['Vector']);r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(.43,.37,.29,1);r.color_ramp.elements[1].color=(.7,.63,.53,1);nt.links.new(noise.outputs['Fac'],r.inputs[0]);nt.links.new(r.outputs[0],p.inputs['Base Color']);bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.00015;bump.inputs['Strength'].default_value=.2;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],p.inputs['Normal'])
ceramic=material('Warm white bathroom ceramic',(.82,.80,.74),.18)
grout=material('Warm grout',(.48,.43,.35),.85)
frame=material('Window frame bronze',(.12,.055,.025),.32,.7)
def block(name,loc,scale,mat,bevel=.001):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(mat)
 if bevel:be=o.modifiers.new('Soft real edges','BEVEL');be.width=bevel;be.segments=3
 return o
block('Bathroom vanity counter',(0,.10,-.015),(1.4,1.4,.03),stone)
block('Background tile grout',(0,.34,.24),(1.3,.025,.48),grout)
for ix in range(-4,4):
 for iz in range(3):block('Warm wall tile',(.16*ix+.08,.321,.08+.16*iz),(.158,.012,.158),ceramic,.0006)
# Vessel basin visible only as an architectural curved rim on the left, no accessories.
verts=[];faces=[];rings=[]
for j in range(25):
 t=j/24;r=.135*math.sin(t*math.pi/2);z=.006+.055*(1-math.cos(t*math.pi/2));rings.append((r,z))
rings +=[(.139,.062),(.143,.06),(.145,.054),(.14,.038),(.128,.017),(.10,.003)]
for r,z in rings:
 for i in range(128):a=i*math.tau/128;verts.append((-.34+r*math.cos(a),.13+r*math.sin(a),z))
for j in range(len(rings)-1):
 for i in range(128):k=j*128+i;kn=j*128+(i+1)%128;faces.append((k,kn,kn+128,k+128))
me=bpy.data.meshes.new('Basin continuous curved surface');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Bathroom basin partial rim',me);S.collection.objects.link(o);o.data.materials.append(ceramic)
for p in me.polygons:p.use_smooth=True
# Product receives only one common rigid pose change.
pivot=Vector((-.075,.105,0));R=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(-58),4,'Z')@Matrix.Translation(-pivot)
for o in product:o.matrix_world=[REDACTED_EMAIL]_world
# Foreground ledge masks the existing white connector, not a geometry edit.
block('Foreground stone ledge',(-.14,-.032,.021),(.46,.09,.042),stone,.002)
# Fine matte observed in 348: a dense grain plus subtle larger-scale roughness, no stain/scratch map.
black=bpy.data.materials['Fine matte black'];nt=black.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
for link in list(nt.links):
 if link.to_node==bs and link.to_socket.name in ['Normal','Roughness']:nt.links.remove(link)
pos=nt.nodes.new('ShaderNodeNewGeometry');grain=nt.nodes.new('ShaderNodeTexNoise');grain.inputs['Scale'].default_value=10000;grain.inputs['Detail'].default_value=2;grain.inputs['Roughness'].default_value=.65;nt.links.new(pos.outputs['Position'],grain.inputs['Vector']);bp=nt.nodes.new('ShaderNodeBump');bp.inputs['Strength'].default_value=.32;bp.inputs['Distance'].default_value=.000028;nt.links.new(grain.outputs['Fac'],bp.inputs['Height']);nt.links.new(bp.outputs[0],bs.inputs['Normal']);mr=nt.nodes.new('ShaderNodeMapRange');mr.inputs['To Min'].default_value=.40;mr.inputs['To Max'].default_value=.55;nt.links.new(grain.outputs['Fac'],mr.inputs['Value']);nt.links.new(mr.outputs[0],bs.inputs['Roughness']);bs.inputs['Base Color'].default_value=(.0045,.005,.006,1)
# Very small grain-linked albedo variation; no large blotches or photographic dirt.
bs.inputs['Specular IOR Level'].default_value=.35
ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.0035,.004,.005,1);ramp.color_ramp.elements[1].color=(.006,.0065,.0075,1);nt.links.new(grain.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
chrome=bpy.data.materials['Studio silver - optical approximation'];nt=chrome.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Roughness'].default_value=.09;bs.inputs['Base Color'].default_value=(.75,.76,.77,1)
pos=nt.nodes.new('ShaderNodeNewGeometry');grain=nt.nodes.new('ShaderNodeTexNoise');grain.inputs['Scale'].default_value=8000;grain.inputs['Detail'].default_value=2;nt.links.new(pos.outputs['Position'],grain.inputs['Vector']);bp=nt.nodes.new('ShaderNodeBump');bp.inputs['Strength'].default_value=.12;bp.inputs['Distance'].default_value=.000006;nt.links.new(grain.outputs['Fac'],bp.inputs['Height']);nt.links.new(bp.outputs[0],bs.inputs['Normal'])
red=bpy.data.materials['Red actuator polymer'];bs=next(n for n in red.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Roughness'].default_value=.23;bs.inputs['Base Color'].default_value=(.36,.002,.012,1)
def area(name,pos,target,energy,size,sy,color=(1,1,1)):
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.name=name;o.data.energy=energy;o.data.color=color;o.data.shape='RECTANGLE';o.data.size=size;o.data.size_y=sy;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
area('Large window daylight',(-.35,-.12,.48),(-.05,.10,.02),12,.22,.38,(1,.97,.92))
area('Neutral right fill',(.28,.05,.36),(-.05,.12,.02),3,.13,.35)
area('Soft rear edge',(-.05,.40,.32),(-.05,.10,.02),4,.30,.08)
# Actual reflection architecture: white wall and narrow dark window mullions.
white=material('Reflection white wall',(.85,.85,.85),.4);dark=material('Reflection dark mullions',(.008,.008,.008),.6)
for i in range(4):
 o=block('Window mullion '+str(i),(-.24+i*.052,.30,.37),(.010,.014,.28),dark,.001);o.visible_camera=False;o.visible_glossy=False
# Broad off-camera luminous window, with the mullions breaking up chrome reflections.
bpy.ops.mesh.primitive_plane_add(size=1,location=(-.07,.24,.39));o=bpy.context.object;o.name='Large physical window reflection';o.scale=(.5,.55,1);o.rotation_euler=(Vector((-.05,.12,.02))-o.location).to_track_quat('Z','Y').to_euler();o.visible_camera=False
m=bpy.data.materials.new('Window radiance');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(1,.98,.94,1);em.inputs[1].default_value=1.0;tc=nt.nodes.new('ShaderNodeTexCoord');sep=nt.nodes.new('ShaderNodeSeparateXYZ');ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.20;ramp.color_ramp.elements[0].color=(.035,.035,.035,1);ramp.color_ramp.elements[1].position=.60;ramp.color_ramp.elements[1].color=(1.8,1.8,1.8,1);nt.links.new(tc.outputs['Generated'],sep.inputs[0]);nt.links.new(sep.outputs['X'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],em.inputs[0]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],out.inputs[0]);o.data.materials.append(m)
# Diagonal window frame shadows across the set.
for i in range(3):
 o=block('Offcamera window shadow slat '+str(i),(-.23+i*.055,-.03,.18),(.009,.55,.012),frame,.0005);o.rotation_euler.z=.45;o.visible_camera=False;o.visible_glossy=False
world=next(n for n in S.world.node_tree.nodes if n.type=='BACKGROUND');world.inputs['Color'].default_value=(.75,.75,.75,1);world.inputs['Strength'].default_value=.27
cam.location=(.025,-.27,.64);target=Vector((-.075,.12,.025));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.30;cam.data.shift_y=.13;cam.data.shift_x=.02
S.view_settings.exposure=0;S.render.resolution_x=S.render.resolution_y=1600 if final else 800;S.render.resolution_percentage=100;S.cycles.samples=192 if final else 40;S.render.image_settings.file_format='PNG';S.render.filepath=str(B/('render1600.png' if final else 'draft.png'));assert before==fingerprint()
(B/'geometry-check.json').write_text(json.dumps({'local_mesh_unchanged':True,'hashes':before,'pose':'common rigid world Z rotation -58deg','no_AI_product_pixels':True},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(B/('圆形花洒_浴室代表图.blend' if final else 'draft-scene.blend')));bpy.ops.render.render(write_still=True)
