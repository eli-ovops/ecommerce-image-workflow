import bpy,math,json
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parent/'renders';bpy.ops.wm.open_mainfile(filepath=str(O/'silver_product_v003.blend'));scene=bpy.context.scene;cam=scene.camera
fm=bpy.data.objects['03 Planar removable face panel'].data.materials[0];im=next(n for n in fm.node_tree.nodes if n.type=='TEX_IMAGE');im.image=bpy.data.images.load(str(O/'face-photo-rectified-v003.png'));im.image.pack()
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'silver_product_v004.blend'))
shots=[('front3q',28,(0,.017,.133),.305,.025,-10),('back3q',145,(0,.017,.133),.305,.025,8),('strictside',90,(0,.017,.133),.305,0,0),('buttonclose',8,(0,.014,.183),.197,.018,0)];receipt=[]
for name,angle,target,scale,elev,roll in shots:
 a=math.radians(angle);cam.location=Vector(target)+Vector((.7*math.sin(a),-.7*math.cos(a),elev));cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.rotation_euler.rotate_axis('Z',math.radians(roll));cam.data.ortho_scale=scale
 scene.render.filepath=str(R/f'{name}-v004.png');print('START',name,flush=True);bpy.ops.render.render(write_still=True)
 receipt.append({'name':name,'camera_location':list(cam.location),'camera_euler_xyz_radians':list(cam.rotation_euler),'orthographic_scale_m':scale,'target':target,'azimuth_degrees':angle,'elevation_offset_m':elev,'roll_degrees':roll,'source_blend':'silver_product_v004.blend'})
 (O/'camera-receipts-v004.json').write_text(json.dumps(receipt,indent=2));print('END',name,flush=True)
