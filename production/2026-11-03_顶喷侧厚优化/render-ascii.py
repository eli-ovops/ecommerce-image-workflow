import bpy, json
from pathlib import Path
from mathutils import Vector, Matrix
P=Path(__file__).resolve().parent
R=P.parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'production/2026-11-03_\u9876\u55b7389\u5206\u5c42\u539a\u5ea6\u4e0e\u6c34\u5e55/native/static-dry-v3.blend'))
sc=bpy.context.scene
shell=bpy.data.objects['Housing_300x200x20']
before=[tuple(v.co) for v in shell.data.vertices]
knob=bpy.data.objects['Outward_pull_knob_concave_face']
mat=bpy.data.materials.new('Original372 knob surface photograph');mat.use_nodes=True
nt=mat.node_tree;nt.nodes.clear()
tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/'production/2026-10-31_\u9876\u55b7\u5b54\u4f4d\u56de\u6e90\u53ef\u63a7\u4fee\u590d/372-front-rectified.jpg'));tex.image.pack()
em=nt.nodes.new('ShaderNodeEmission');em.inputs['Strength'].default_value=.8
out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(tex.outputs['Color'],em.inputs['Color']);nt.links.new(em.outputs[0],out.inputs['Surface'])
knob.data.materials.append(mat);mi=len(knob.data.materials)-1
uv=knob.data.uv_layers.active or knob.data.uv_layers.new(name='Original photo XY')
for face in knob.data.polygons:
 if face.normal.z>.12 and min(knob.data.vertices[i].co.z for i in face.vertices)>.011:
  face.material_index=mi
 for li in face.loop_indices:
  v=knob.data.vertices[knob.data.loops[li].vertex_index].co
  uv.data[li].uv=((v.x+.15)/.3,(v.y+.1)/.2)
c=sc.camera;c.location=(.34,-.035,.6)
z=c.location.normalized();x=Vector((0,1,0)).cross(z).normalized();y=z.cross(x).normalized()
c.rotation_euler=Matrix((x,y,z)).transposed().to_euler();c.data.ortho_scale=.39
sc.render.resolution_x=1300;sc.render.resolution_y=1700;sc.render.resolution_percentage=100
sc.cycles.samples=64
sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA'
sc.render.filepath=str(P/'native/product-v1.png')
assert before==[tuple(v.co) for v in shell.data.vertices]
xyz=[[v.co[i] for v in shell.data.vertices] for i in range(3)]
(P/'native/geometry.json').write_text(json.dumps({'shell_dimensions_mm':[(max(a)-min(a))*1000 for a in xyz],'shell_vertices_unchanged':True,'camera_location':list(c.location),'knob_original_photo_surface':True,'limitations':['Auxiliary shell reconstructed from photographs, not manufacturing CAD','Face photograph retains original baked lighting','No same-angle original photograph available']},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/product-v1.blend'))
bpy.ops.render.render(write_still=True)
