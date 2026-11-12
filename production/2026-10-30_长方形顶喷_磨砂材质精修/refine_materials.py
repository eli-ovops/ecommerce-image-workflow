import bpy,json,hashlib,struct
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'输入场景.blend'))
s=bpy.context.scene
names=['Housing_300x200x20','Observed_white_protective_cap','Outward_pull_knob_concave_face','Rear_connector_visible_envelope_UNCONFIRMED_thread','Recessed_panel_with_true_through_holes']
def fingerprint():
 d={}
 for name in names:
  o=bpy.data.objects[name];h=hashlib.sha256()
  for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
  for f in o.data.polygons:h.update(struct.pack('<I',len(f.vertices)));h.update(struct.pack('<'+'I'*len(f.vertices),*f.vertices))
  d[name]={'sha256':h.hexdigest(),'world':[list(r) for r in o.matrix_world],'dimensions_mm':[v*1000 for v in o.dimensions],'modifiers':[(m.type,getattr(m,'width',None),getattr(m,'segments',None)) for m in o.modifiers]}
 return d
before=fingerprint()
# Native shader detail in physical object coordinates, no vertex displacement.
panel=bpy.data.objects[names[-1]];m=panel.data.materials[0].copy();m.name='Panel fine matte grain — source 372 376 382';panel.data.materials[0]=m
nt=m.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');bs=nt.nodes.new('ShaderNodeBsdfPrincipled');nt.links.new(bs.outputs['BSDF'],out.inputs['Surface']);bs.inputs['Metallic'].default_value=.04
tex=nt.nodes.new('ShaderNodeTexCoord');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=4500;noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.65;nt.links.new(tex.outputs['Object'],noise.inputs['Vector'])
ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.15;ramp.color_ramp.elements[0].color=(.016,.019,.023,1);ramp.color_ramp.elements[1].position=.85;ramp.color_ramp.elements[1].color=(.032,.037,.043,1);nt.links.new(noise.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
rough=nt.nodes.new('ShaderNodeMapRange');rough.inputs['From Min'].default_value=0;rough.inputs['From Max'].default_value=1;rough.inputs['To Min'].default_value=.38;rough.inputs['To Max'].default_value=.57;nt.links.new(noise.outputs['Fac'],rough.inputs['Value']);nt.links.new(rough.outputs[0],bs.inputs['Roughness'])
bevel=nt.nodes.new('ShaderNodeBevel');bevel.inputs['Radius'].default_value=.00014;bevel.samples=4
bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.65;bump.inputs['Distance'].default_value=.00009;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bevel.outputs['Normal'],bump.inputs['Normal']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
red=bpy.data.objects[names[2]].data.materials[0].copy();red.name='Red knob saturated satin — source 372';bpy.data.objects[names[2]].data.materials[0]=red
r=next(n for n in red.node_tree.nodes if n.type=='BSDF_PRINCIPLED');r.inputs['Base Color'].default_value=(.75,.009,.0015,1);r.inputs['Roughness'].default_value=.31;r.inputs['Specular IOR Level'].default_value=.28
# Mirror shell retains its base material; only neutral illumination changes its reflection.
def aim(o,t):
 from mathutils import Vector
 o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
key=bpy.data.objects['Neutral large window'];key.location=(-.28,-.10,.19);aim(key,(0,0,0));key.data.energy=3.3;key.data.size=.30;key.data.size_y=.16;key.data.color=(1,1,1)
bpy.data.lights['Warm rim'].energy=.55;bpy.data.lights['White strip for silver'].energy=1.1
bg=next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.3,.3,.3,1);bg.inputs[1].default_value=.20
stone=bpy.data.materials.get('Set warm ivory stone');t=next(n for n in stone.node_tree.nodes if n.type=='BSDF_PRINCIPLED');t.inputs['Base Color'].default_value=(.42,.37,.30,1)
s.cycles.samples=128;s.cycles.use_denoising=True
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=97
assert before==fingerprint()
s.camera=bpy.data.objects['01_银色完整顶喷']
bpy.ops.wm.save_as_mainfile(filepath=str(P/'磨砂精修_同一商品场景.blend'))
records={}
for name in ['01_银色完整顶喷','02_静态红钮近景_非拉出']:
 s.camera=bpy.data.objects[name];s.render.filepath=str(P/(name+'_磨砂精修.jpg'));records[name]=fingerprint();assert records[name]==before;bpy.ops.render.render(write_still=True)
(P/'geometry-preservation.json').write_text(json.dumps({'before':before,'after':fingerprint(),'renders':records,'all_equal':all(v==before for v in records.values()),'shader_bump_only_no_displacement':True},ensure_ascii=False,indent=2))
(P/'material-changes.json').write_text(json.dumps({'panel':{'evidence':[372,376,382],'coordinates':'Object metres','noise_scale':4500,'noise_detail':2,'base_color_linear_range':[[.016,.019,.023],[.032,.037,.043]],'roughness_range':[.38,.57],'bump_strength':.65,'bump_distance_m':.00009,'shader_bevel_m':.00014},'red_knob':{'source':372,'base_color_linear':[.75,.009,.0015],'roughness':.31,'specular_ior_level':.28},'silver_shell':'original mirror shader unchanged; neutral light reflection','lighting':'neutral grazing key; reduced warm rim; neutral world','stage':'less saturated ivory; original warm gold direction retained','precision':'visual estimates, not measured surface roughness'},ensure_ascii=False,indent=2))
print('REFINED_PAIR_DONE',flush=True)
