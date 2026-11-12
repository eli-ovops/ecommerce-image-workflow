import bpy,math,json,sys,hashlib,struct
from pathlib import Path
from mathutils import Vector,Matrix
B=Path(__file__).resolve().parent;args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];final='final' in args;which=next((x for x in args if x in ['A','B','C']),None)
for code in ([which] if which else ['A','B','C']):
 bpy.ops.wm.open_mainfile(filepath=str(B/'sources/baseline.blend'));S=bpy.context.scene;cam=S.camera;floor=bpy.data.objects['Neutral seamless studio'];bs=next(n for n in floor.data.materials[0].node_tree.nodes if n.type=='BSDF_PRINCIPLED');product=[o for o in S.objects if o.type=='MESH' and o.name[:2].isdigit()]
 before={o.name:hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in o.data.vertices)).hexdigest() for o in product}
 if code=='A':
  bs.inputs['Base Color'].default_value=(.75,.67,.55,1);cam.data.ortho_scale=.325;cam.data.shift_y=.135
  # Warm stone surface, restrained micro relief; no accessory props.
  nt=floor.data.materials[0].node_tree;tc=nt.nodes.new('ShaderNodeTexCoord');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=240;nt.links.new(tc.outputs['Object'],noise.inputs['Vector']);bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.00012;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],bs.inputs['Normal'])
 elif code=='B':
  bs.inputs['Base Color'].default_value=(.004,.003,.002,1);bs.inputs['Roughness'].default_value=.42;cam.data.ortho_scale=.315;cam.data.shift_y=.11
  pivot=Vector((-.075,.105,0));R=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(-68),4,'Z')@Matrix.Translation(-pivot)
  for o in product:o.matrix_world=[REDACTED_EMAIL]_world
  # Keep neutral product light, copper edge ambience belongs to the set.
  bpy.ops.object.light_add(type='AREA',location=(.3,.25,.32));o=bpy.context.object;o.name='Copper set rim';o.data.energy=5;o.data.color=(1,.6,.3);o.data.shape='RECTANGLE';o.data.size=.16;o.data.size_y=.4;o.rotation_euler=(Vector((-.08,.1,.02))-o.location).to_track_quat('-Z','Y').to_euler()
 else:
  bs.inputs['Base Color'].default_value=(.65,.59,.50,1);cam.data.ortho_scale=.26;cam.data.shift_y=.20
 if code in ['A','B']:
  def block(name,loc,scale,color,rot=0,visible=True):
   bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.rotation_euler.z=rot;o.visible_camera=visible
   m=bpy.data.materials.new(name);m.use_nodes=True;p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.7;o.data.materials.append(m);be=o.modifiers.new('Stone edge softness','BEVEL');be.width=.0015;be.segments=3
   return o
  if code=='A':
   block('Foreground stone step',(0,-.035,.020),(.6,.09,.04),(.66,.56,.43))
   block('Warm bathroom wall',(-.255,.16,.10),(.025,.8,.2),(.72,.64,.53))
   for i in range(3):block('Window shadow bar '+str(i),(-.20+i*.045,.03,.11),(.012,.6,.012),(.1,.1,.1),.45,False)
   bpy.ops.object.light_add(type='AREA',location=(-.38,-.20,.48));l=bpy.context.object;l.name='Soft window daylight';l.data.energy=4;l.data.shape='RECTANGLE';l.data.size=.09;l.data.size_y=.20;l.rotation_euler=(Vector((-.08,.1,0))-l.location).to_track_quat('-Z','Y').to_euler()
  else:
   next(n for n in S.world.node_tree.nodes if n.type=='BACKGROUND').inputs['Strength'].default_value=.25
   slab=block('Foreground graphite ledge',(-.14,-.035,.022),(.38,.085,.044),(.009,.006,.004),-.15)
 after={o.name:hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in o.data.vertices)).hexdigest() for o in product};assert before==after
 S.render.resolution_x=S.render.resolution_y=1600 if final else 800;S.cycles.samples=144 if final else 40;S.render.resolution_percentage=100;S.render.filepath=str(B/(code+('-render.png' if final else '-draft.png')));S['status']='THREE_ADS_USER_REVIEW_PENDING';S.render.image_settings.file_format='PNG'
 (B/(code+'-geometry.json')).write_text(json.dumps({'local_mesh_unchanged':before==after,'hashes':after,'pose_change':'One common rigid Z rotation -68deg' if code=='B' else 'unchanged','camera_ortho':cam.data.ortho_scale,'camera_shift_y':cam.data.shift_y},ensure_ascii=False,indent=2))
 from bpy_extras.object_utils import world_to_camera_view
 bpy.context.view_layer.update();points={}
 for key,prefix in [('red','06 '),('selector','07 ')]:
  obj=next(o for o in product if o.name.startswith(prefix));c=sum((Vector(v) for v in obj.bound_box),Vector())/8;v=world_to_camera_view(S,cam,obj.matrix_world@c);points[key]=[v.x*1600,(1-v.y)*1600]
 (B/(code+'-points.json')).write_text(json.dumps(points))
 if final:bpy.ops.wm.save_as_mainfile(filepath=str(B/(code+'-scene.blend')))
 bpy.ops.render.render(write_still=True)
