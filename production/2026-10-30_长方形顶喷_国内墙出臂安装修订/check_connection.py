import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'墙出臂安装.blend'))
s=bpy.context.scene;rig=bpy.data.objects['Product_RIG_RIGID_ONLY'];arm=bpy.data.objects['SET_ONLY continuous wall arm'];points=arm.data.splines[0].points
end=arm.matrix_world@Vector(points[-1].co[:3]);previous=arm.matrix_world@Vector(points[-2].co[:3]);local=rig.matrix_world.inverted()@end
axis=rig.matrix_world.to_3x3()@Vector((0,0,-1));toward_product=(end-previous).normalized();alignment=toward_product.dot(-axis.normalized())
assert (local-Vector((0,0,-.038))).length<1e-6 and alignment>.999999
deps=bpy.context.evaluated_depsgraph_get();origin=s.camera.matrix_world.translation
hits=[]
for i in range(96):
 a=math.tau*i/96;target=rig.matrix_world@Vector((.013*math.cos(a),.013*math.sin(a),-.0397));ray=target-origin
 hit,loc,normal,face,obj,matrix=s.ray_cast(deps,origin,ray.normalized(),distance=ray.length+.0001)
 hits.append({'sample':i,'first_object':obj.name if hit else None,'target_distance_mm':(loc-target).length*1000 if hit else None,'visible_connector':bool(hit and obj.name=='Connector_open_metal_envelope_ESTIMATED' and (loc-target).length<.001)})
result={'arm_endpoint_product_local_m':list(local),'axis_alignment_dot':alignment,'opening_lip_z_m':-.0397,'estimated_insertion_m':.0017,'visible_metal_lip_samples_of_96':sum(h['visible_connector'] for h in hits),'samples':hits,'scope':'Finite camera-ray check of estimated visible metal lip, not physical thread fit or full installation approval.'}
(P/'connection-camera-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='samples'}))
