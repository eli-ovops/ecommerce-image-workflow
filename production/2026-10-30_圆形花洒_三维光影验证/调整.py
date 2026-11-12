import bpy
from pathlib import Path
p=Path(__file__).resolve().parent
src=p.parent/'2026-10-28_圆形花洒_实拍三维融合代表图/圆形花洒_浴室代表图.blend'
bpy.ops.wm.open_mainfile(filepath=str(src))
s=bpy.context.scene
for name in ('Large window daylight','Neutral right fill','Soft rear edge'):
 o=bpy.data.objects.get(name)
 if o:
  o.data.energy *= {'Large window daylight':0.7,'Neutral right fill':1.5,'Soft rear edge':0.75}[name]
chrome=bpy.data.materials.get('Studio silver - optical approximation')
if chrome:
 b=next(n for n in chrome.node_tree.nodes if n.type=='BSDF_PRINCIPLED');b.inputs['Roughness'].default_value=.16
black=bpy.data.materials.get('Fine matte black')
if black:
 b=next(n for n in black.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); b.inputs['Specular IOR Level'].default_value=.3
s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.cycles.samples=48
s.render.image_settings.file_format='PNG';s.render.filepath=str(p/'同场景验证.png')
bpy.ops.wm.save_as_mainfile(filepath=str(p/'三维光影验证.blend'))
bpy.ops.render.render(write_still=True)
