import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent
O=P/'lighting-refine';(O/'native').mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(P/'native/product-v2.blend'))
s=bpy.context.scene
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
for mat in bpy.data.materials:
 if mat.use_nodes:
  for node in mat.node_tree.nodes:
   if node.type=='EMISSION':node.inputs['Strength'].default_value=1
for o in bpy.data.objects:
 if o.type=='LIGHT':
  o.data.energy*=.055
  o.data.color=(1,.94,.85)
  if o.name=='Water backlight':o.hide_render=True
bg=next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND')
bg.inputs['Color'].default_value=(.25,.235,.21,1);bg.inputs['Strength'].default_value=.35
shell=bpy.data.objects['Housing_300x200x20']
for mat in shell.data.materials:
 for node in mat.node_tree.nodes:
  if node.type=='BSDF_PRINCIPLED':node.inputs['Roughness'].default_value=.24
s.render.resolution_x=1300;s.render.resolution_y=1700;s.cycles.samples=64
s.render.filepath=str(O/'native/product.png')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'native/product.blend'))
(O/'lighting-changes.json').write_text(json.dumps({'view':'Standard','exposure':0,'photo_emission_strength':1,'light_energy_multiplier':.055,'water_backlight_disabled':True,'shell_roughness':.24,'unchanged':['shell mesh','face mesh and UV','knob geometry and UV','camera','300x200x20mm dimensions']},indent=2))
bpy.ops.render.render(write_still=True)
