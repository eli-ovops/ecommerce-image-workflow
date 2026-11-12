import bpy, json, math
from mathutils import Vector
from pathlib import Path
p=Path('/Volumes/EXTERNAL/电商 作图工作流/production/2026-11-04_方形三键花洒_普通出水图')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(n,c,metal=0,rough=.4):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;b=next(x for x in m.node_tree.nodes if x.type=='BSDF_PRINCIPLED');b.inputs['Base Color'].default_value=(*c,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough;return m
plate=mat('仅作方位的黑色平面',(.025,.03,.035));white=mat('喷孔示意',(.8,.83,.86));water=mat('水束方向示意',(.62,.84,1),.0,.15)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,.07,3.9));o=bpy.context.object;o.name='仅方向示意-非商品几何';o.dimensions=(2.7,.14,3.1);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);b=o.modifiers.new('圆角','BEVEL');b.width=.22;b.segments=8;o.modifiers.new('法线','WEIGHTED_NORMAL');o.data.materials.append(plate)
a=json.loads(Path('/Volumes/EXTERNAL/电商 作图工作流/production/2026-11-04_方形三键花洒_三维统一成像验证/465_白嘴提取.json').read_text())['items']
for it in a:
 x=(600-it['source_y'])/210;z=2.45+(740-it['source_x'])/210
 # 线条从平面前方的喷孔中心向外，不在面板上绘制。
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=.048,location=(x,-.055,z));bpy.context.object.data.materials.append(white)
 cu=bpy.data.curves.new('离开喷孔的连续水线','CURVE');cu.dimensions='3D';cu.bevel_depth=.009;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(1);sp.points[0].co=(x,-.075,z,1);sp.points[1].co=(x,-4.2,z-.42,1);obj=bpy.data.objects.new('水线示意',cu);bpy.context.collection.objects.link(obj);obj.data.materials.append(water)
world=bpy.context.scene.world;world.color=(.23,.23,.23)
def area(loc,energy,size):
 d=bpy.data.lights.new('光','AREA');d.energy=energy;d.size=size;o=bpy.data.objects.new('光',d);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,3))-o.location).to_track_quat('-Z','Y').to_euler()
area((2,-5,9),900,5);area((-5,-3,6),500,4)
c=bpy.data.cameras.new('camera');o=bpy.data.objects.new('camera',c);bpy.context.collection.objects.link(o);o.location=(8,-8,7);o.rotation_euler=(Vector((0,-1,3.4))-o.location).to_track_quat('-Z','Y').to_euler();c.type='ORTHO';c.ortho_scale=7;bpy.context.scene.camera=o
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG';s.render.filepath=str(p/'三维水束方向示意.png');bpy.ops.wm.save_as_mainfile(filepath=str(p/'三维水束方向示意.blend'));bpy.ops.render.render(write_still=True)
