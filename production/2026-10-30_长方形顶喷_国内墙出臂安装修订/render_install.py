import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'输入浴室场景.blend'))
s=bpy.context.scene;rig=bpy.data.objects['Product_RIG_RIGID_ONLY']
rig.rotation_euler=(math.radians(150),0,0);rig.location=(0,-.10,2.15);bpy.context.view_layer.update()
for o in list(bpy.data.objects):
 if o.name.startswith('SET_ONLY'):bpy.data.objects.remove(o,do_unlink=True)
ma=bpy.data.materials['Generic fixture brushed steel']
# A scene-only wall arm follows the connector axis; no product connector deformation.
tip=rig.matrix_world@Vector((0,0,-.038))
axis=rig.rotation_euler.to_matrix()@Vector((0,0,-1))
theta=math.atan2(axis.z,axis.y);radius=.05
end=tip+axis*.11
start=Vector((0,end.y+radius*math.sin(theta),end.z+radius*(1-math.cos(theta))))
wall=Vector((0,.35,start.z))
d=bpy.data.curves.new('Generic wall arm continuous curve','CURVE');d.dimensions='3D';d.resolution_u=24;d.bevel_depth=.0105;d.bevel_resolution=5
points=[wall,start]+[Vector((0,start.y-radius*math.sin(theta*i/24),start.z-radius*(1-math.cos(theta*i/24)))) for i in range(1,25)]+[tip]
sp=d.splines.new('POLY');sp.points.add(len(points)-1)
for p,co in zip(sp.points,points):p.co=(*co,1)
o=bpy.data.objects.new('SET_ONLY continuous wall arm',d);s.collection.objects.link(o);o.data.materials.append(ma)
bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.027,depth=.012,location=wall);f=bpy.context.object;f.name='SET_ONLY wall flange';f.rotation_euler=(math.pi/2,0,0);f.data.materials.append(ma)
for p in f.data.polygons:p.use_smooth=len(p.vertices)==4
camera=s.camera;camera.location=(.20,-.86,2.42);target=Vector((0,.02,2.18));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=58;camera.data.dof.focus_distance=(target-camera.location).length;camera.data.dof.aperture_fstop=13
preview='--preview' in sys.argv;s.render.resolution_percentage=50 if preview else 100;s.cycles.samples=24 if preview else 128
s.render.filepath=str(P/('墙出臂安装_preview_v2.jpg' if preview else '墙出臂安装.jpg'))
if not preview:bpy.ops.wm.save_as_mainfile(filepath=str(P/'墙出臂安装.blend'))
bpy.ops.render.render(write_still=True)
(P/'connection-placement.json').write_text(json.dumps({'connector_axis_world':list(axis),'arm_terminal_world':list(tip),'arm_terminal_product_local_m':[0,0,-.038],'connector_open_end_product_local_m':[0,0,-.0397],'description':'Arm terminal enters visible opening by 1.7mm, axis aligned. This is visual scene assembly only; thread and engineering compatibility UNKNOWN. Product rig is rotated as one rigid assembly; no part changed.'},indent=2))
