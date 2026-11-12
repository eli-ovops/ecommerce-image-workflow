import bpy,bmesh,json,math,hashlib,struct,sys
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;ROOT=O.parents[2];R=O.parent/'renders';S=ROOT/'production/2026-10-24_实物建模/blender/v010a/shower_black_clay_v010a.blend'
bpy.ops.wm.open_mainfile(filepath=str(S));scene=bpy.context.scene
body=bpy.data.objects['01 Unified exterior - shared cylinder and neck boundary']
def geom_hash(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
 for p in o.data.polygons:h.update(struct.pack('<%di'%len(p.vertices),*p.vertices))
 return h.hexdigest()
source_geom=geom_hash(body)
# Build physically lit appearance only; no edit to approved body vertices or polygon topology.
def material(name,color,metal=0,rough=.3):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.node_tree.nodes.clear();p=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface']);p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
silver=material('Silver visual appearance - not a material certification',(.72,.75,.78),1,.16)
black=material('Black front insert',(.018,.021,.023),0,.37)
red=material('Red central descaling control',(.55,.008,.018),0,.24)
white=material('White nozzle rings from SIL001 positions',(.86,.88,.81),0,.32)
body.data.materials.clear();body.data.materials.append(silver);body.data.materials.append(black)
for f in body.data.polygons:
 c=f.center;z=c.z;x=c.x
 zone=(z>=.12 and abs(x)<.015+.64*(z-.12)) or ((x/.015)**2+((z-.12)/.018)**2<1)
 f.material_index=1 if zone and z>.102 and f.normal.y<-.65 else 0
for name in ['04 Lower three-mode selector button','05 Connector exterior | specification UNKNOWN']:
 ob=bpy.data.objects[name];ob.data.materials.clear();ob.data.materials.append(silver)
ctrl=bpy.data.objects['04 Central control aligned to face plane'];ctrl.data.materials.clear();ctrl.data.materials.append(red)
C=Vector((0,.006562611103057861,.2));axis=Vector((0,.9912921786308289,.13168083131313324));up=Vector((0,-.13168083131313324,.9912921786308289));right=Vector((1,0,0))
face=bpy.data.objects['03 Planar removable face panel'];face.data.materials.clear();fm=material('Photo sourced black face with exact visible outer holes',(.02,.02,.02),0,.42);face.data.materials.append(fm)
n=fm.node_tree.nodes;l=fm.node_tree.links;p=next(nod for nod in n if nod.type=='BSDF_PRINCIPLED');tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(O/'face-photo-rectified.png'));tex.image.pack();l.new(tex.outputs['Color'],p.inputs['Base Color'])
uv=face.data.uv_layers.new(name='SIL001 rectified projection')
for poly in face.data.polygons:
 for li in poly.loop_indices:
  co=face.data.vertices[face.data.loops[li].vertex_index].co-C;uv.data[li].uv=(.5+co.x/.1252,.5+co.dot(up)/.1252)
# Actual detected nozzle positions. Each shallow ring is geometry, not an invented regular grid.
holes=json.loads((O/'face-source-and-holes.json').read_text())['holes'];vs=[];fs=[];N=24
for h in holes:
 x,v=h['plane_mm'];r=h['radius_mm']*.001;center=C+right*x*.001+up*v*.001
 start=len(vs)
 for rr,dd in [(r*.95,-.00083),(r*.93,-.00105),(r*.35,-.00105),(r*.33,-.00085)]:
  for j in range(N):a=2*math.pi*j/N;vs.append(center+right*rr*math.cos(a)+up*rr*math.sin(a)+axis*dd)
 for k in range(3):
  for j in range(N):fs.append((start+k*N+j,start+k*N+(j+1)%N,start+(k+1)*N+(j+1)%N,start+(k+1)*N+j))
me=bpy.data.meshes.new('SIL001 detected white annuli mesh');me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new('144 photo-positioned shallow white nozzle rings',me);scene.collection.objects.link(ob);me.materials.append(white)
for f in me.polygons:f.use_smooth=True
# Simplified exterior thread ridges, all silver. No interface standard claimed.
conn=bpy.data.objects['05 Connector exterior | specification UNKNOWN'];co=[v.co for v in conn.data.vertices];cx=sum(v.x for v in co)/len(co);cy=sum(v.y for v in co)/len(co);zmin=min(v.z for v in co);zmax=max(v.z for v in co)
curve=bpy.data.curves.new('Simplified silver thread helix','CURVE');curve.dimensions='3D';curve.resolution_u=1;curve.bevel_depth=.00034;curve.bevel_resolution=3;sp=curve.splines.new('POLY');count=720;sp.points.add(count-1)
for i,pnt in enumerate(sp.points):
 t=i/(count-1);a=t*2*math.pi*5;pnt.co=(cx+.01055*math.cos(a),cy+.01055*math.sin(a),zmin+.0008+t*(zmax-zmin-.0016),1)
thread=bpy.data.objects.new('Silver thread exterior - unspecified size',curve);scene.collection.objects.link(thread);curve.materials.append(silver)
# Remove historical lights and set a studio suitable for polished silver reflections.
for ob in list(bpy.data.objects):
 if ob.type=='LIGHT':bpy.data.objects.remove(ob,do_unlink=True)
world=bpy.data.worlds.new('Neutral studio world');scene.world=world;world.use_nodes=True;next(n for n in world.node_tree.nodes if n.type=='BACKGROUND').inputs['Color'].default_value=(.38,.41,.45,1);next(n for n in world.node_tree.nodes if n.type=='BACKGROUND').inputs['Strength'].default_value=.45
T=Vector((0,.016,.14))
def area(name,pos,power,size,sizey):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='RECTANGLE';d.size=size;d.size_y=sizey;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=pos;o.rotation_euler=(T-o.location).to_track_quat('-Z','Y').to_euler()
area('Large softbox left',(-.28,-.38,.34),45,.22,.43)
area('Strip reflection right',(.27,-.16,.22),28,.065,.4)
area('Back edge softbox',(.12,.30,.31),45,.2,.35)
area('Top fill',(-.05,.02,.58),18,.3,.25)
scene.render.engine='CYCLES';scene.cycles.samples=96;scene.cycles.use_denoising=True;scene.cycles.max_bounces=6
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='METAL'
scene.cycles.device='GPU';scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='16';scene.render.resolution_x=2000;scene.render.resolution_y=2000;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=0
cam=scene.camera;cam.data.type='ORTHO'
def camera(angle,target,scale,elev=0,roll=0):
 a=math.radians(angle);cam.location=Vector(target)+Vector((.7*math.sin(a),-.7*math.cos(a),elev));cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.rotation_euler.rotate_axis('Z',math.radians(roll));cam.data.ortho_scale=scale
camera(28,(0,.017,.133),.305,.025,-10)
report={'source_blend':str(S),'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'source_body_geometry_sha256':source_geom,'current_body_geometry_sha256':geom_hash(body),'body_geometry_exactly_unchanged':source_geom==geom_hash(body),'nozzle_count':len(holes),'nozzle_source':'face-source-and-holes.json','renderer':'Cycles Metal GPU','samples':96,'appearance_claim':'Silver visual shading only, no physical material or interface standard claim','routing':{'target_model':'gpt-6-astra','target_effort':'high','actual_model':'UNKNOWN','actual_effort':'UNKNOWN','speed':'UNKNOWN'}}
(O/'build-evidence.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'silver_product_v001.blend'))
scene.render.filepath=str(R/'front3q.png');bpy.ops.render.render(write_still=True)
print('FRONT3Q_READY',R/'front3q.png')
