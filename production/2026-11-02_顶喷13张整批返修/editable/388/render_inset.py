import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;S=P.parent/'2026-11-02_391安装仰视单张实验'
bpy.ops.wm.open_mainfile(filepath=str(P/'388-installed-source.blend'));sc=bpy.context.scene
for o in list(bpy.data.objects):
 if o.type=='CURVE':bpy.data.objects.remove(o,do_unlink=True)
rig=bpy.data.objects['Product_RIG_RIGID_ONLY'];rig.location=(0,0,0);rig.rotation_euler=(0,0,math.radians(76))
# Native single photo face; no new holes or copied cutout outline.
face=bpy.data.objects['ONLY_PHOTO_FACE_NO_DUPLICATE_CIRCLES'];nt=face.data.materials[0].node_tree
for n in nt.nodes:
 if n.type=='EMISSION':n.inputs['Strength'].default_value=.8
for o in bpy.data.objects:
 if o.type=='LIGHT':o.hide_render=True
m=bpy.data.objects['Housing_300x200x20'].data.materials[0];bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Roughness'].default_value=.23
# More subdued chrome/knob reflections than the installed experiment.
red=bpy.data.objects['Outward_pull_knob_concave_face'].data.materials[0];rb=next(n for n in red.node_tree.nodes if n.type=='BSDF_PRINCIPLED');rb.inputs['Roughness'].default_value=.38

def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def light(name,loc,power,sx,sy,col):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='RECTANGLE';d.size=sx;d.size_y=sy;d.color=col;o=bpy.data.objects.new(name,d);sc.collection.objects.link(o);o.location=loc;aim(o,(0,0,0))
light('Warm soft key',(-.22,.1,.35),2.5,.25,.4,(1,.88,.73));light('Narrow silver edge',(.28,-.1,.18),1.2,.04,.32,(1,.96,.89));light('Neutral fill',(0,-.35,.28),.8,.4,.4,(.86,.93,1))
bg=next(n for n in sc.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.16,.13,.10,1);bg.inputs[1].default_value=.22
cam=sc.camera;cam.location=(0,-.08,.6);aim(cam,(0,0,0));cam.data.ortho_scale=.40
sc.view_settings.exposure=-.8;sc.render.resolution_x=900;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.cycles.samples=64;sc.render.film_transparent=True
sc.render.filepath=str(P/'inset-native-render.png');bpy.ops.wm.save_as_mainfile(filepath=str(P/'388-inset.blend'));bpy.ops.render.render(write_still=True)
(P/'inset-record.json').write_text(json.dumps({'source_blend':str(P/'388-installed-source.blend'),'face':'single original372 photo texture, no second hole mesh','rig_rotation_deg':[0,0,76],'mesh_changes':False,'changes':'camera, rigid pose, shell roughness and lighting; no new product geometry','water_removed_from_inset_only':True},indent=2))
