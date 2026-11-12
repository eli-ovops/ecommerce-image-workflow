import bpy,json
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(B/'圆形花洒_retry02.blend'))
for name in ['01 Continuous calibrated exterior','02 Continuous black face and selector surround','10 Dark aperture backing']:
 o=bpy.data.objects[name]; print(name,'MAT',[(m.name,[(n.type,list(n.inputs['Base Color'].default_value)) for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED']) for m in o.data.materials])
 for x,z in [(0,.150),(.02,.153),(.035,.165)]:
  hit,loc,n,idx=o.ray_cast(Vector((x,-1,z)),Vector((0,1,0)));print(x,z,hit,list(loc))
