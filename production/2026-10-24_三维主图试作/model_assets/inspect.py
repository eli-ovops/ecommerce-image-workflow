import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='/Volumes/EXTERNAL/电商 作图工作流/production/2026-10-24_实物建模/blender/v010a/shower_black_clay_v010a.blend')
for o in bpy.data.objects:
 if o.type=='MESH':print(o.name,tuple(o.location),tuple(o.dimensions))
p=bpy.context.preferences.addons['cycles'].preferences
try:p.compute_device_type='METAL';p.get_devices();print('DEVICES',[(d.name,d.type) for d in p.devices])
except Exception as e:print(e)
