import bpy
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parent/'renders';bpy.ops.wm.open_mainfile(filepath=str(O/'silver_product_v002.blend'));scene=bpy.context.scene
m=bpy.data.materials.new('Independent plain silver controls and connector');m.use_nodes=True;m.node_tree.nodes.clear();p=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Base Color'].default_value=(.72,.75,.78,1);p.inputs['Metallic'].default_value=1;p.inputs['Roughness'].default_value=.16;out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface'])
for name in ['04 Lower three-mode selector button','05 Connector exterior | specification UNKNOWN','Silver thread exterior - unspecified size']:
 ob=bpy.data.objects[name];ob.data.materials.clear();ob.data.materials.append(m)
fm=bpy.data.objects['03 Planar removable face panel'].data.materials[0];im=next(n for n in fm.node_tree.nodes if n.type=='TEX_IMAGE');im.image=bpy.data.images.load(str(O/'face-photo-rectified-v002.png'));im.image.pack()
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'silver_product_v003.blend'));scene.render.filepath=str(R/'front3q-v003.png');bpy.ops.render.render(write_still=True);print('V003_FRONT_READY',flush=True)
