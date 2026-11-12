"""Photo-constrained editable exterior candidate. Run with Blender background --python.
No CAD/metrology claim. All scene units below millimetre candidates, converted to m.
"""
import bpy, math, json, os, sys
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent
PARAM_PATH=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else BASE/'parameters-v004.json'
P=json.loads(PARAM_PATH.read_text())
OUT=BASE/P['version'];(OUT/'renders').mkdir(exist_ok=True,parents=True);(OUT/'turntable_frames').mkdir(exist_ok=True,parents=True)
HR=P['head_radius'];HZ=P['head_center_z'];TOP=P['total_length']
# Monotonic cubic Hermite interpolation avoids overshoot on section stations.
def curve(tab,x,end_slope=None):
 n=len(tab); xs=[p[0] for p in tab]; ys=[p[1] for p in tab]
 d=[(ys[i+1]-ys[i])/(xs[i+1]-xs[i]) for i in range(n-1)]
 m=[d[0]]+[0 if d[i-1]*d[i]<=0 else 2*d[i-1]*d[i]/(d[i-1]+d[i]) for i in range(1,n-1)]+[d[-1]]
 if end_slope is not None:m[-1]=end_slope
 if x<=xs[0]:return ys[0]
 if x>=xs[-1]:return ys[-1]
 i=next(i for i in range(n-1) if xs[i]<=x<=xs[i+1]);h=xs[i+1]-xs[i];t=(x-xs[i])/h
 return (2*t**3-3*t*t+1)*ys[i]+(t**3-2*t*t+t)*h*m[i]+(-2*t**3+3*t*t)*ys[i+1]+(t**3-t*t)*h*m[i+1]
def front(z):return curve(P['front_profile_z_y'],z)
def width(z):return curve(P['width_profile_z_halfwidth'],z)
def rear(z):return curve(P['back_profile_z_y'],z)
def mat(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
 b=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) or m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');b.inputs['Base Color'].default_value=(*c,1);b.inputs['Roughness'].default_value=.8
 return m
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for col in list(bpy.data.collections):
 if col.name!='Collection' and col.users==0:bpy.data.collections.remove(col)
clay=mat('Clay - exterior',(0.58,.60,.61)); panelmat=mat('Clay - separate face insert',(.44,.46,.47)); buttonmat=mat('Clay - controls',(.34,.36,.37))
product=bpy.data.collections.new('PRODUCT | editable exterior candidate');bpy.context.scene.collection.children.link(product)
def mesh_obj(name,vs,fs,material):
 mesh=bpy.data.meshes.new(name+' mesh');mesh.from_pydata([(x*.001,y*.001,z*.001) for x,y,z in vs],[],fs);mesh.update()
 o=bpy.data.objects.new(name,mesh);product.objects.link(o);o.data.materials.append(material)
 for p in mesh.polygons:p.use_smooth=True
 return o
zs=[9,9.25,9.7]+list(range(11,264))+[264,264.5,264.8,264.95,265]
N=128;vs=[];fs=[]
for z in zs:
 w=width(z);f=front(z);b=rear(z);t=b-f
 blend=max(0,min(1,(w-16)/20));blend=blend*blend*(3-2*blend)
 exponent=1*(1-blend)+.12*blend
 taper=min(1,math.sqrt(max(0.0001,(265-z)/.75)))
 for j in range(N):
  th=2*math.pi*j/N;co=math.cos(th);s=math.sin(th);x=w*co
  if s<0:y=f+t/2*(1-abs(s)**exponent)
  else:y=b-t/2*(1-abs(s)**(1*(1-blend)+.35*blend))
  yc=(f+b)/2;y=yc+(y-yc)*taper
  vs.append((x,y,z))
for i in range(len(zs)-1):
 for j in range(N):a=i*N+j;b=i*N+(j+1)%N;fs.append((a,b,b+N,a+N))
fs.append(tuple(reversed(range(N))));fs.append(tuple((len(zs)-1)*N+j for j in range(N)))
shell=mesh_obj('01 Continuous head-neck-handle shell',vs,fs,clay)
shell['construction']='Single cross-section loft, not disc plus straight handle'
shell['evidence']='P02-P05, P07; V01 f03,f07,f12; nominal scale P09-P13'
# Flat circular insert follows head plane. Separate object, not the shell geometry source.
def disk(name,r,z0,depth,off,material,rx=1):
 vs=[];fs=[];n=128
 for back in [0,1]:
  for j in range(n):
   a=2*math.pi*j/n;x=r*math.cos(a)*rx;z=z0+r*math.sin(a);vs.append((x,front(z)+off+back*depth,z))
 fs.extend([tuple(reversed(range(n))),tuple(n+j for j in range(n))])
 for j in range(n):fs.append((j,(j+1)%n,(j+1)%n+n,j+n))
 ob=mesh_obj(name,vs,fs,material);bev=ob.modifiers.new('Small edge round','BEVEL');bev.width=.00045;bev.segments=3
 return ob
face=disk('02 Removable face panel - holes pending',62.6,200,1.1,-.8,panelmat)
face['limitation']='No hole layout invented; front nozzle centers pending P01 extraction'
# central annular press button with measured visual ratio ~18mm /130mm.
vs=[];fs=[];seg=96
for r,off in [(9,-1.2),(9,-2.3),(6.0,-3.5),(3.0,-3.5),(2.8,-1.3)]:
 for j in range(seg):
  a=2*math.pi*j/seg;x=r*math.cos(a);z=200+r*math.sin(a);vs.append((x,front(z)+off,z))
for k in range(4):
 for j in range(seg):fs.append((k*seg+j,k*seg+(j+1)%seg,(k+1)*seg+(j+1)%seg,(k+1)*seg+j))
mesh_obj('03 Central descaling press button | gray clay',vs,fs,buttonmat)
# rounded trapezoid switch, independent object, from P01/P08.
vs=[];fs=[];seg=96
for d,sc in [(0,1),(2.8,1),(3.6,.93)]:
 for j in range(seg):
  a=2*math.pi*j/seg;c=math.cos(a);s=math.sin(a)
  z=121+14.5*math.copysign(abs(s)**.65,s)*sc
  x=10.5*math.copysign(abs(c)**.65,c)*sc*(1+.08*(z-121)/14.5)
  vs.append((x,front(z)-.7-d,z))
for k in range(2):
 for j in range(seg):fs.append((k*seg+j,k*seg+(j+1)%seg,(k+1)*seg+(j+1)%seg,(k+1)*seg+j))
fs.append(tuple(2*seg+j for j in range(seg)));switch=mesh_obj('04 Lower three-mode selector button',vs,fs,buttonmat)
bev=switch.modifiers.new('Control edge round','BEVEL');bev.width=.0006;bev.segments=3
# Connector exterior only; concentric relief is visual placeholder, not thread specification.
vs=[];fs=[];N=96
rings=[(0,9.8),(.6,10.5),(8.6,10.5),(9,10.3)]
for z,r in rings:
 for j in range(N):a=2*math.pi*j/N;vs.append((r*math.cos(a),(front(9)+rear(9))/2+r*math.sin(a),z))
for k in range(len(rings)-1):
 for j in range(N):fs.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
# bottom annulus, open hole; no interior mechanism
for j in range(N):a=2*math.pi*j/N;vs.append((4.8*math.cos(a),(front(9)+rear(9))/2+4.8*math.sin(a),0))
for j in range(N):fs.append((j,4*N+j,4*N+(j+1)%N,(j+1)%N))
con=mesh_obj('05 Connector exterior | specification UNKNOWN',vs,fs,clay);con['limitation']='No standard, pitch or functional fit claimed; exterior envelope only'
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='MILLIMETERS'
scene.render.engine='BLENDER_WORKBENCH';sh=scene.display.shading
sh.light='STUDIO';sh.studiolight_rotate_z=.3;sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.curvature_ridge_factor=1.2;sh.curvature_valley_factor=.8
sh.show_object_outline=False;sh.background_type='WORLD';scene.world.color=(.82,.82,.82)
scene.view_settings.view_transform='Standard';scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=94
scene.render.resolution_x=1000;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.film_transparent=False
cam_data=bpy.data.cameras.new('Inspection orthographic camera');cam=bpy.data.objects.new('Inspection orthographic camera',cam_data);scene.collection.objects.link(cam);scene.camera=cam;cam_data.type='ORTHO';cam_data.ortho_scale=.31
cam_data.lens=70
TARGET=Vector((0,.017,.1325))
def camera(angle,elev=0):
 a=math.radians(angle);cam.location=TARGET+Vector((.7*math.sin(a),-.7*math.cos(a),elev));cam.rotation_euler=(TARGET-cam.location).to_track_quat('-Z','Y').to_euler()
# saved scene defaults to oblique; cameras produce neutral non-advertising views.
camera(35,.035)
for area in bpy.context.screen.areas if bpy.context.screen else []:
 if area.type=='VIEW_3D':area.spaces.active.region_3d.view_distance=.4
readme=bpy.data.texts.new('READ ME - CANDIDATE NOT METROLOGY')
readme.write(P['version']+' / 2026-10-24\nBlack SKU only. Editable photo-constrained exterior candidate.\nNominal scale: total 265mm, head width130mm; photo tape estimates not CAD truth.\nv003 rejected; v004 traced P03/P04/P01 shell envelope. Nozzle positions deferred; connector specification UNKNOWN.\nOriginal sources outside blend: ../sources/ and ../source-manifest.json.\nRebuild: blender --background --python build_model.py\nSee parameters-'+P['version']+'.json and self-check.md.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/('shower_black_clay_'+P['version']+'.blend')))
summary={'blender_version':bpy.app.version_string,'objects':[],'nominal_bbox_mm':[130, None,265], 'mesh_validation':[]}
for o in product.objects:
 summary['objects'].append({'name':o.name,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)})
 summary['mesh_validation'].append({'name':o.name,'mesh_validate_changed':o.data.validate(verbose=False)})
(OUT/'model-data.json').write_text(json.dumps(summary,indent=2))
for name,angle,elev in [('front',0,0),('left',90,0),('right',-90,0)]:
 camera(angle,elev);scene.render.filepath=str(OUT/'renders'/f'{name}.jpg');bpy.ops.render.render(write_still=True)
# actual 360 degree sequence, 72 views. Encode at 12fps for a six-second inspection turntable.
scene.render.resolution_x=720;scene.render.resolution_y=900
for f in range(72 if P.get('render_turntable',True) else 0):
 camera(f*5,.025);scene.render.filepath=str(OUT/'turntable_frames'/f'{f:03d}.jpg');bpy.ops.render.render(write_still=True)
print('MODEL_AND_RENDERS_COMPLETE',OUT)
