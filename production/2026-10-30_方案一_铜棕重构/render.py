import bpy, json, hashlib, struct, sys, math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
p=Path(__file__).resolve().parent
source=p.parent/'2026-10-30_方案一_三维反射构图/三维方案一.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
obs=[o for o in s.objects if o.type=='MESH' and o.name[:2].isdigit()]
def fp():
 return {o.name:hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in o.data.vertices)+b''.join(struct.pack('<I',i) for f in o.data.polygons for i in f.vertices)+str(tuple(tuple(x) for x in o.matrix_world)).encode()).hexdigest() for o in obs}
before=fp()
for o in list(s.objects):
 if o not in obs: bpy.data.objects.remove(o,do_unlink=True)
pts=[[REDACTED_EMAIL] for o in obs for v in o.data.vertices]
lo=Vector(tuple(min(v[i] for v in pts) for i in range(3)));hi=Vector(tuple(max(v[i] for v in pts) for i in range(3)));center=(lo+hi)/2
print('BOUNDS',tuple(lo),tuple(hi),flush=True)
def mat(name,color,rough,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;return m
bronze=mat('Set - muted bronze',(0.045,.022,.014),.42,.25)
stone=mat('Set - dark cocoa satin',(.036,.021,.015),.49)
def cube(name,loc,size,material,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 if bevel:m=o.modifiers.new('Soft machined set edges','BEVEL');m.width=bevel;m.segments=4;o.modifiers.new('Set normals','WEIGHTED_NORMAL')
 return o
# Entire product rests on a broad slab; no foreground element crosses the handle.
cube('Full presentation slab',(center.x,center.y,lo.z-.014),(.36,.32,.028),bronze,.003)
cube('Continuous cocoa floor',(0,0,lo.z-.045),(200,200,.03),stone)
bpy.ops.object.camera_add(location=center+Vector((.18,-.28,.60)));cam=bpy.context.object;cam.name='Hero camera';cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.32;s.camera=cam
bpy.context.view_layer.update()
def bounds():
 q=[world_to_camera_view(s,cam,o.matrix_world@Vector(v)) for o in obs for v in o.bound_box];return [min(v.x for v in q),max(v.x for v in q),min(v.y for v in q),max(v.y for v in q)]
b=bounds();cam.data.ortho_scale*=max(b[1]-b[0],b[3]-b[2])/.89;bpy.context.view_layer.update();b=bounds();cam.data.shift_x=(b[0]+b[1])/2-.5;cam.data.shift_y=(b[2]+b[3])/2-.5
s.world.use_nodes=True;next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND').inputs[0].default_value=(.12,.10,.085,1);next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND').inputs[1].default_value=.35
def light(name,offset,power,sx,sy,color):
 bpy.ops.object.light_add(type='AREA',location=center+Vector(offset));o=bpy.context.object;o.name=name;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler();o.data.energy=power;o.data.shape='RECTANGLE';o.data.size=sx;o.data.size_y=sy;o.data.color=color
light('Long neutral softbox',(-.25,-.12,.40),10,.16,.48,(1,.95,.88))
light('Cool silver edge',(.28,.12,.28),8,.06,.38,(.86,.92,1))
light('Soft frontal panel fill',(.02,-.28,.5),3,.32,.30,(1,1,1))
light('Warm set wash',(-.05,.34,.4),5,.28,.3,(1,.7,.45))
# Texture coordinates in world metres: fine moulded grain, not silhouette displacement.
m=bpy.data.materials['Fine matte black'];n=m.node_tree.nodes;links=m.node_tree.links;bs=n.get('Principled BSDF')
for link in list(bs.inputs['Base Color'].links):links.remove(link)
bs.inputs['Base Color'].default_value=(.009,.012,.014,1)
bs.inputs['Specular IOR Level'].default_value=.22
for link in list(bs.inputs['Roughness'].links):links.remove(link)
bs.inputs['Roughness'].default_value=.64
geo=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=6500;noise.inputs['Detail'].default_value=2
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.26;bump.inputs['Distance'].default_value=.000045
links.new(geo.outputs['Position'],noise.inputs['Vector']);links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bs.inputs['Normal'])
silver=bpy.data.materials['Studio silver - optical approximation'].node_tree.nodes['Principled BSDF'];silver.inputs['Roughness'].default_value=.105
red=bpy.data.materials['Red actuator polymer'].node_tree.nodes['Principled BSDF'];red.inputs['Base Color'].default_value=(.48,.004,.012,1);red.inputs['Roughness'].default_value=.26
bpy.context.view_layer.update();assert fp()==before
b=bounds();assert min(b[0],b[2])>.04 and max(b[1],b[3])<.96,b
s.view_settings.exposure=-1.3
final='--final' in sys.argv
s.render.engine='CYCLES';s.cycles.samples=160 if final else 40;s.cycles.use_denoising=True
s.render.resolution_x=s.render.resolution_y=1600 if final else 800;s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=96;s.render.filepath=str(p/('铜棕代表图.jpg' if final else 'draft.jpg'))
(p/'geometry-audit.json').write_text(json.dumps({'product_fingerprints':before,'unchanged_mesh_topology_world_transform':fp()==before,'bounds':b,'source':str(source),'requested_model':'gpt-6-astra','requested_effort':'medium','actual_model':'UNKNOWN'},ensure_ascii=False,indent=2))
if final:bpy.ops.wm.save_as_mainfile(filepath=str(p/'铜棕代表图.blend'))
bpy.ops.render.render(write_still=True)
