import bpy,math,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P.parent/'399-preview.blend'));s=bpy.context.scene
def fingerprint():
 out={}
 for o in bpy.data.objects['Product_RIG_RIGID_ONLY'].children:
  if o.type=='MESH':
   h=hashlib.sha256()
   for v in o.data.vertices:h.update(struct.pack('3f',*v.co))
   for f in o.data.polygons:h.update(str(tuple(f.vertices)).encode())
   out[o.name]=h.hexdigest()
 return out
before=fingerprint()
p=bpy.data.objects['Recessed_panel_with_true_through_holes'];m=bpy.data.materials.new('372 original photo color and roughness UV');m.use_nodes=True;p.data.materials[0]=m;n=m.node_tree.nodes;l=m.node_tree.links;b=next(x for x in n if x.type=='BSDF_PRINCIPLED');b.inputs['Metallic'].default_value=0
for filename,socket,space in [('372-color-registered.png','Base Color','sRGB'),('372-roughness-registered.png','Roughness','Non-Color')]:
 t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(P/filename));t.image.colorspace_settings.name=space;t.image.pack();l.new(t.outputs['Color'],b.inputs[socket])
uv=n.new('ShaderNodeUVMap');uv.uv_map='Planar_original372_registration'
for t in n:
 if t.type=='TEX_IMAGE':l.new(uv.outputs['UV'],t.inputs['Vector'])
co=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=6000;l.new(co.outputs['Object'],noise.inputs['Vector']);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.000025;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],b.inputs['Normal'])
def aim(o,t=(0,0,0)):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
# Broad neutral source makes silver readable; existing narrow light retains edge contrast.
key=bpy.data.objects['Neutral grazing key'];key.location=(-.14,-.12,.42);key.data.energy=12;key.data.size=.38;key.data.size_y=.55;aim(key)
fill=bpy.data.objects['Soft fill'];fill.data.energy=4
rim=bpy.data.objects['Silver long reflection'];rim.data.energy=7;rim.data.size=.16;rim.data.size_y=.50
bg=next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.4,.4,.4,1);bg.inputs[1].default_value=.35
s.view_settings.exposure=0;s.cycles.samples=32;s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=97
assert fingerprint()==before
(P/'geometry-unchanged.json').write_text(json.dumps({'unchanged':True,'product_mesh_sha256':before,'scope':'Identical vertices and face indices to parent399-preview.blend; geometry classification inherited from checked source.'},indent=2))
s.render.filepath=str(P/'399-preview.jpg');bpy.ops.wm.save_as_mainfile(filepath=str(P/'399-preview.blend'));bpy.ops.render.render(write_still=True)
rig=bpy.data.objects['Product_RIG_RIGID_ONLY'];cam=s.camera;cam.location=rig.matrix_world@Vector((-.075,.02,.23));aim(cam,rig.matrix_world@Vector((-.075,.02,.007)));cam.data.ortho_scale=.085;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=80;s.render.filepath=str(P/'399-detail.jpg');bpy.ops.render.render(write_still=True)
