import bpy,json,hashlib,struct,sys
from pathlib import Path
p=Path(__file__).resolve().parent
source=p.parent/'2026-10-30_方案一_铜棕重构/铜棕代表图.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
obs=[o for o in s.objects if o.type=='MESH' and o.name[:2].isdigit()]
def fp():
 return {o.name:hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in o.data.vertices)+b''.join(struct.pack('<I',i) for f in o.data.polygons for i in f.vertices)+str(tuple(tuple(x) for x in o.matrix_world)).encode()).hexdigest() for o in obs}
def camera():
 c=s.camera;return {'matrix':list(map(list,c.matrix_world)),'type':c.data.type,'scale':c.data.ortho_scale,'shift':[c.data.shift_x,c.data.shift_y],'lens':c.data.lens}
before=fp();cam=camera()
# Reflection-only neutral surround lifts the black mirror bands without extra direct panel illumination.
n=s.world.node_tree.nodes;l=s.world.node_tree.links
out=next(x for x in n if x.type=='OUTPUT_WORLD');old=out.inputs['Surface'].links[0].from_socket
ray=n.new('ShaderNodeLightPath');fill=n.new('ShaderNodeBackground');fill.name='Neutral reflection surround';fill.inputs['Color'].default_value=(.65,.68,.72,1);fill.inputs['Strength'].default_value=.7
mix=n.new('ShaderNodeMixShader');l.new(ray.outputs['Is Glossy Ray'],mix.inputs[0]);l.new(old,mix.inputs[1]);l.new(fill.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs['Surface'])
m=bpy.data.materials['Fine matte black'];n=m.node_tree.nodes;l=m.node_tree.links;bs=next(x for x in n if x.type=='BSDF_PRINCIPLED')
geo=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.name='Moulded grain - world metre scale';noise.inputs['Scale'].default_value=2800;noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.65
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.42;bump.inputs['Distance'].default_value=.000055
l.new(geo.outputs['Position'],noise.inputs['Vector']);l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],bs.inputs['Normal'])
ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.007,.009,.011,1);ramp.color_ramp.elements[1].color=(.014,.018,.021,1);l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.57;bs.inputs['Specular IOR Level'].default_value=.28
silver=next(x for x in bpy.data.materials['Studio silver - optical approximation'].node_tree.nodes if x.type=='BSDF_PRINCIPLED');silver.inputs['Roughness'].default_value=.16
red=next(x for x in bpy.data.materials['Red actuator polymer'].node_tree.nodes if x.type=='BSDF_PRINCIPLED');red.inputs['Base Color'].default_value=(.19,.001,.006,1);red.inputs['Roughness'].default_value=.34;red.inputs['Specular IOR Level'].default_value=.25
assert fp()==before and camera()==cam
final='--final' in sys.argv;s.cycles.samples=192 if final else 48;s.render.resolution_x=s.render.resolution_y=1600 if final else 1000
s.render.filepath=str(p/('固定机位材质修订.jpg' if final else 'draft.jpg'))
(p/'geometry-audit.json').write_text(json.dumps({'product_fingerprints':before,'camera':cam,'geometry_topology_transform_unchanged':fp()==before,'camera_unchanged':camera()==cam,'source':str(source),'actual_model':'UNKNOWN','requested_model':'gpt-6-astra','requested_effort':'medium'},ensure_ascii=False,indent=2))
if final:bpy.ops.wm.save_as_mainfile(filepath=str(p/'固定机位材质修订.blend'))
bpy.ops.render.render(write_still=True)
