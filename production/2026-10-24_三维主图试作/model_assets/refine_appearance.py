import bpy,math,json
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parent/'renders';bpy.ops.wm.open_mainfile(filepath=str(O/'silver_product_v001.blend'));scene=bpy.context.scene
for ob in bpy.data.objects:
 if ob.type=='LIGHT':ob.data.energy/=24
scene.world.node_tree.nodes[0] if False else None
body=bpy.data.objects['01 Unified exterior - shared cylinder and neck boundary'];silver=body.data.materials[0]
for f in body.data.polygons:f.material_index=0
n=silver.node_tree.nodes;l=silver.node_tree.links;out=next(z for z in n if z.type=='OUTPUT_MATERIAL');ps=next(z for z in n if z.type=='BSDF_PRINCIPLED');black=n.new('ShaderNodeBsdfPrincipled');black.inputs['Base Color'].default_value=(.009,.011,.013,1);black.inputs['Roughness'].default_value=.38
tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(O/'neck-black-mask.png'));tex.image.pack();tex.extension='CLIP';tex.interpolation='Linear'
g=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(g.outputs['Position'],sep.inputs[0]);comb=n.new('ShaderNodeCombineXYZ')
def mathnode(op,a,b):
 q=n.new('ShaderNodeMath');q.operation=op
 if isinstance(a,(float,int)):q.inputs[0].default_value=a
 else:l.new(a,q.inputs[0])
 if isinstance(b,(float,int)):q.inputs[1].default_value=b
 else:l.new(b,q.inputs[1])
 return q.outputs[0]
u=mathnode('ADD',mathnode('DIVIDE',sep.outputs['X'],.13),.5);v=mathnode('DIVIDE',mathnode('SUBTRACT',sep.outputs['Z'],.09),.08);l.new(u,comb.inputs['X']);l.new(v,comb.inputs['Y']);l.new(comb.outputs[0],tex.inputs['Vector'])
ns=n.new('ShaderNodeSeparateXYZ');l.new(g.outputs['Normal'],ns.inputs[0]);front=mathnode('LESS_THAN',ns.outputs['Y'],-.65);fac=mathnode('MULTIPLY',front,tex.outputs['Color']);mix=n.new('ShaderNodeMixShader');l.new(fac,mix.inputs[0]);l.new(ps.outputs[0],mix.inputs[1]);l.new(black.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs['Surface'])
# Darken only the black face substrate uniformly; source holes stay in the same UV locations.
fm=bpy.data.objects['03 Planar removable face panel'].data.materials[0];fn=fm.node_tree.nodes;fl=fm.node_tree.links;im=next(z for z in fn if z.type=='TEX_IMAGE');p=next(z for z in fn if z.type=='BSDF_PRINCIPLED');mul=fn.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;mul.inputs[2].default_value=(.45,.45,.45,1);fl.new(im.outputs['Color'],mul.inputs[1]);fl.new(mul.outputs[0],p.inputs['Base Color'])
p.inputs['Specular IOR Level'].default_value=.25
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
scene.render.resolution_percentage=100;scene.cycles.samples=96;bpy.ops.wm.save_as_mainfile(filepath=str(O/'silver_product_v002.blend'))
scene.render.filepath=str(R/'front3q-v002.png');bpy.ops.render.render(write_still=True);print('V002_FRONT_READY',flush=True)
