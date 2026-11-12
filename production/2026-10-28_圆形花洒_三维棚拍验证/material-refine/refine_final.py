import bpy,json,hashlib,struct
from pathlib import Path
B=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(B/'sources/baseline.blend'));S=bpy.context.scene
# Fingerprint original mesh coordinates/topology, modifiers and world transform.
def fingerprints():
 out={}
 for o in S.objects:
  if o.type!='MESH' or not o.name[:2].isdigit():continue
  h=hashlib.sha256()
  for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
  for p in o.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
  out[o.name]={'mesh':h.hexdigest(),'matrix':[list(r) for r in o.matrix_world],'modifiers':[(m.name,m.type) for m in o.modifiers]}
 return out
before=fingerprints();camera={'matrix':[list(r) for r in S.camera.matrix_world],'ortho_scale':S.camera.data.ortho_scale}
black=bpy.data.objects['02 Unified perforated panel'].data.materials[0];nodes=black.node_tree.nodes;links=black.node_tree.links;bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');noise=next(n for n in nodes if n.type=='TEX_NOISE');bump=next(n for n in nodes if n.type=='BUMP');ramp=next(n for n in nodes if n.type=='MAP_RANGE')
noise.inputs['Scale'].default_value=1800;noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.6
bump.inputs['Strength'].default_value=.4;bump.inputs['Distance'].default_value=.0001
ramp.inputs['To Min'].default_value=.43;ramp.inputs['To Max'].default_value=.59
bs.inputs['Specular IOR Level'].default_value=.28
silver=bpy.data.objects['01 Rebuilt continuous silver exterior and seat'].data.materials[0];next(n for n in silver.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Roughness'].default_value=.165
card=bpy.data.objects['Broad white reflection card'];card.scale.x*=1.65;card.scale.y*=1.35
r=next(n for n in card.data.materials[0].node_tree.nodes if n.type=='VALTORGB');r.color_ramp.interpolation='EASE';r.color_ramp.elements[0].position=0;r.color_ramp.elements[0].color=(.45,.45,.45,1);r.color_ramp.elements[1].position=1;r.color_ramp.elements[1].color=(1.3,1.3,1.3,1)
# Wider physical strip softens a hard chrome highlight without changing exposure.
S.objects['Narrow side strip'].data.size=.095;S.objects['Narrow side strip'].data.energy=3
flag=S.objects['Slim dark reflection flag'];flag.scale.x=.05
S.cycles.samples=160;S.render.filepath=str(B/'candidate-02.png');S.render.image_settings.file_format='PNG';S['status']='MATERIAL_REFINEMENT_USER_REVIEW_PENDING'
after=fingerprints();assert before==after
(B/'geometry-fingerprints.json').write_text(json.dumps({'before':before,'after':after,'identical':before==after,'camera':camera,'scope':'Product mesh coordinates/topology, modifier identity and world transforms; no geometry edits'},ensure_ascii=False,indent=2))
(B/'parameters.json').write_text(json.dumps({'black_noise_scale_per_m':1800,'black_bump_strength':.4,'black_bump_distance_m':.0001,'black_roughness_range':[.43,.59],'silver_roughness':.165,'reflection_card_size':list(card.scale),'strip_width_m':.095,'exposure_unchanged':S.view_settings.exposure,'samples':160,'actual_model':'UNKNOWN','requested_model':'gpt-6-astra','requested_effort':'medium'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(B/'圆形花洒_材质精修.blend'));bpy.ops.render.render(write_still=True)
