import bpy,math,sys,json,hashlib,struct
from pathlib import Path
from mathutils import Matrix,Vector
B=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
final='final' in args
codes=[x for x in args if x in ['D','E','F']] or ['D','E','F']
for code in codes:
 bpy.ops.wm.open_mainfile(filepath=str(B/'sources/baseline.blend'));S=bpy.context.scene;cam=S.camera
 product=[o for o in S.objects if o.type=='MESH' and o.name[:2].isdigit()]
 before={o.name:hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in o.data.vertices)).hexdigest() for o in product}
 floor=bpy.data.objects['Neutral seamless studio'];p=next(n for n in floor.data.materials[0].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 p.inputs['Base Color'].default_value=(.55,.46,.35,1) if code!='D' else (.018,.012,.009,1)
 def aim(pos,target):
  cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
 if code=='D':
  aim((.28,.18,.22),(-.12,.17,.025));cam.data.ortho_scale=.195;cam.data.shift_y=.12;cam.data.shift_x=.03
 elif code=='E':
  # Single common rigid flip, with a common lift placing the rear presentation on the floor.
  R0=Matrix.Rotation(math.radians(35),4,'Z')@Matrix.Rotation(-math.pi/2,4,'X');delta=[REDACTED_EMAIL](math.pi,4,'Z')@R0.inverted()
  for o in product:o.matrix_world=[REDACTED_EMAIL]_world
  zmin=min(([REDACTED_EMAIL]).z for o in product for v in o.data.vertices)
  lift=Matrix.Translation((0,0,.0003-zmin))
  for o in product:o.matrix_world=[REDACTED_EMAIL]_world
  aim((.02,-.23,.52),(-.075,.105,.025));cam.data.ortho_scale=.315;cam.data.shift_y=.13
 else:
  aim((-.10,-.08,.57),(-.12,.174,.035));cam.data.ortho_scale=.19;cam.data.shift_y=.15
 # Physical foreground stone masks connector only, continuous set with real shadows.
 if code=='E':
  bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-.038,.015));o=bpy.context.object;o.name='Foreground stone plinth';o.scale=(.65,.09,.03)
  m=bpy.data.materials.new('Plinth');m.use_nodes=True;q=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');q.inputs['Base Color'].default_value=(.04,.025,.016,1) if code=='D' else (.5,.4,.29,1);q.inputs['Roughness'].default_value=.65;o.data.materials.append(m);be=o.modifiers.new('Soft edge','BEVEL');be.width=.001;be.segments=3
 if code in ['D','E']:
  # Large physical gradient card in the reflected camera direction, no material/exposure change.
  bpy.data.objects['Broad white reflection card'].hide_render=True
  center=Vector((-.12,.17,.04));v=(cam.location-center).normalized();r=Vector((-v.x,-v.y,v.z));pos=center+r*.45
  bpy.ops.mesh.primitive_plane_add(size=1,location=pos);card=bpy.context.object;card.name='Broad gradient reflection card '+code;card.rotation_euler=(center-pos).to_track_quat('Z','Y').to_euler();card.scale=(.50,.55,1);card.visible_camera=False
  mat=bpy.data.materials.new('Physical white-to-charcoal reflection surface');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');em=nt.nodes.new('ShaderNodeEmission');tc=nt.nodes.new('ShaderNodeTexCoord');sep=nt.nodes.new('ShaderNodeSeparateXYZ');ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.23;ramp.color_ramp.elements[0].color=(.004,.004,.004,1);ramp.color_ramp.elements[1].position=.53;ramp.color_ramp.elements[1].color=(2.5,2.5,2.5,1);nt.links.new(tc.outputs['Generated'],sep.inputs[0]);nt.links.new(sep.outputs['X'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],em.inputs[0]);nt.links.new(em.outputs[0],out.inputs[0]);card.data.materials.append(mat)
 S.render.resolution_x=S.render.resolution_y=1600 if final else 800;S.render.resolution_percentage=100;S.cycles.samples=144 if final else 32
 S.render.image_settings.file_format='PNG';S.render.filepath=str(B/(code+('-render.png' if final else '-draft.png')))
 assert before=={o.name:hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in o.data.vertices)).hexdigest() for o in product}
 (B/(code+'-geometry.json')).write_text(json.dumps({'local_mesh_unchanged':True,'hashes':before},indent=2))
 if final:bpy.ops.wm.save_as_mainfile(filepath=str(B/(code+'-scene.blend')))
 bpy.ops.render.render(write_still=True)
