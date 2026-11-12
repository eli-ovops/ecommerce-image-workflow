import bpy,json
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(B/'圆形花洒_retry02.blend'));S=bpy.context.scene
panel=bpy.data.objects['02 Continuous black face and selector surround'];m=panel.modifiers.get('Rounded lower insert edge')
if m:panel.modifiers.remove(m)
# Measured ray test found old backing behind actual shell at shoulder (not merely exposure).
shell=bpy.data.objects['01 Continuous calibrated exterior'];back=bpy.data.objects['10 Dark aperture backing'];changed=0
for v in back.data.vertices:
 hit,loc,n,idx=shell.ray_cast(Vector((v.co.x,-1,v.co.z)),Vector((0,1,0)))
 if hit and v.co.y>loc.y-.00008:v.co.y=loc.y-.00008;changed+=1
back.data.update()
black=panel.data.materials[0];p=black.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.0035,.0045,.006,1);p.inputs['Specular IOR Level'].default_value=.10
for n in black.node_tree.nodes:
 if n.type=='TEX_NOISE':n.inputs['Scale'].default_value=4500
 if n.type=='MAP_RANGE':n.inputs['To Min'].default_value=.48;n.inputs['To Max'].default_value=.66
red=bpy.data.objects['06 Red descaling actuator'].data.materials[0];p=red.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.3,.002,.008,1);p.inputs['Roughness'].default_value=.31;p.inputs['Specular IOR Level'].default_value=.3
flag=bpy.data.objects['Slim dark reflection flag'];flag.location.x-=.07;flag.scale.x=.04
S.render.filepath=str(B/'candidate-02.png');S['single_targeted_correction']='Shell ray-fitted dark backing, panel/red response, discard defective lower bevel, slim flag position';bpy.ops.wm.save_as_mainfile(filepath=str(B/'圆形花洒_retry02.blend'))
(B/'correction.json').write_text(json.dumps({'count':1,'backing_vertices_corrected':changed,'cause':'Backing behind chrome shell in lower shoulder, confirmed ray samples in inspect.log','exposure_unchanged':S.view_settings.exposure,'new_product_deformation':False,'discarded_lower_insert_bevel':True},indent=2));bpy.ops.render.render(write_still=True)
