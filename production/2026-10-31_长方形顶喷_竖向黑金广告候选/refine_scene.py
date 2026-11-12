import bpy,sys,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'advertising.blend'));s=bpy.context.scene
s.view_settings.exposure=-1.35
bpy.data.lights['Left sculpting window'].energy=3.5
stone=bpy.data.materials['Dark marble architecture']
for n in stone.node_tree.nodes:
 if n.type=='VALTORGB':
  n.color_ramp.elements[0].position=.994;n.color_ramp.elements[1].position=.999
  n.color_ramp.elements[1].color=(.055,.050,.040,1)
 if n.type=='BSDF_PRINCIPLED':n.inputs['Roughness'].default_value=.42
# Dark enclosed cavity appearance prevents a silver reflection from looking like a plug.
# Only the existing inward-facing rear shell polygon gets a dark shader; no new part.
sh=bpy.data.objects['Housing_300x200x20'];m=bpy.data.materials.new('Unobserved inner cavity shadow - visualization only');m.use_nodes=True
b=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');b.inputs['Base Color'].default_value=(.003,.003,.003,1);b.inputs['Roughness'].default_value=.9
sh.data.materials.append(m);count=0
for f in sh.data.polygons:
 if all(sh.data.vertices[i].co.z<-.007 for i in f.vertices) and f.normal.z>.5:f.material_index=len(sh.data.materials)-1;count+=1
print('INNER_CAVITY_POLYGONS',count,flush=True)
# Hidden clearance accommodates the existing connector while the upper shell leans on stone.
rig=bpy.data.objects['Product_RIG_RIGID_ONLY'];c=rig.matrix_world@Vector((0,0,-.025));wall=bpy.data.objects['Rear stone support and wall']
bpy.ops.mesh.primitive_cube_add(size=1,location=(c.x,wall.location.y,c.z));cut=bpy.context.object;cut.dimensions=(.075,.20,.075);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
mod=wall.modifiers.new('Concealed connector clearance','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.context.view_layer.objects.active=wall;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
s.render.resolution_percentage=100;s.cycles.samples=256;s.render.filepath=str(P/'upright-advertising.jpg')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'upright-advertising.blend'))
if '--preview' in sys.argv:s.render.resolution_percentage=50;s.cycles.samples=40;s.render.filepath=str(P/'scene-preview-v2.jpg')
bpy.ops.render.render(write_still=True)
