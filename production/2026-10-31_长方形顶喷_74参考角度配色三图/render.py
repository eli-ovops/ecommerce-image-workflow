import bpy,math,sys
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
preview='--preview' in sys.argv
views=[('01_warm_front',(.22,-.33,.53),.38,(.13,.055,.026),0),('02_blue_side',(.13,-.52,.17),.365,(.11,.23,.32),0),('03_dark_back',(-.22,-.30,.49),.38,(.014,.032,.055),math.pi)]
def aim(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
for label,campos,scale,color,angle in views:
 bpy.ops.wm.open_mainfile(filepath=str(P/'input.blend'));s=bpy.context.scene
 rig=bpy.data.objects['Product_RIG_RIGID_ONLY'];keep={rig,*rig.children}
 for o in list(bpy.data.objects):
  if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
 rig.rotation_euler=(angle,0,0);rig.location=(0,0,0)
 # A plain seamless surface with a concealed relief for the rear connector/front knob.
 m=bpy.data.materials.new('Original seamless color');m.use_nodes=True
 bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.58
 bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,-.065));floor=bpy.context.object;floor.name='Seamless stage';floor.dimensions=(200,200,.11);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);floor.data.materials.append(m)
 bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=.032,depth=.14,location=(0,0,-.025));cutter=bpy.context.object
 mod=floor.modifiers.new('Concealed product clearance','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter;bpy.context.view_layer.objects.active=floor;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
 def area(name,loc,energy,size,sy,target=(0,0,0)):
  d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='RECTANGLE';d.size=size;d.size_y=sy
  o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;aim(o,target);return o
 area('Large neutral key',(-.32,-.18,.60),14,.46,.60)
 area('Long silver edge',(0,.26,.26),5,.50,.10)
 area('Side neutral strip',(.34,-.13,.16),3,.08,.45)
 if angle:area('Back broad reflection',(.12,.23,.43),3,.16,.52)
 world=bpy.data.worlds.new('Neutral studio world');world.use_nodes=True;s.world=world
 bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.22,.24,.28,1);bg.inputs['Strength'].default_value=.28
 d=bpy.data.cameras.new('Product camera');d.type='ORTHO';d.ortho_scale=scale;d.clip_start=.001;d.clip_end=300
 cam=bpy.data.objects.new('Product camera',d);s.collection.objects.link(cam);cam.location=campos;aim(cam,(0,0,0));s.camera=cam
 s.view_settings.exposure-=1.8
 s.render.engine='CYCLES';s.cycles.samples=24 if preview else 128;s.cycles.use_denoising=True
 s.render.resolution_x=1600;s.render.resolution_y=1600;s.render.resolution_percentage=50 if preview else 100
 s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=97
 s.render.filepath=str(P/(label+('_preview' if preview else '')+'.jpg'))
 bpy.context.view_layer.update()
 if not preview:bpy.ops.wm.save_as_mainfile(filepath=str(P/(label+'.blend')))
 bpy.ops.render.render(write_still=True)
