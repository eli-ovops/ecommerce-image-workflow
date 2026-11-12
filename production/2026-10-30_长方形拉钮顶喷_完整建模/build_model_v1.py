"""Blender 5.2; native bpy only. Run: blender -b --python build_model.py.
All design inputs in mm, converted to metres. Photo-derived dimensions are estimates.
"""
import bpy, bmesh, math, json, csv
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.length_unit='MILLIMETERS'

def mesh(name,verts,faces,mat=None):
 m=bpy.data.meshes.new(name);m.from_pydata([tuple(a*.001 for a in v) for v in verts],[],faces);m.update()
 bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free()
 ob=bpy.data.objects.new(name,m);scene.collection.objects.link(ob)
 if mat:ob.data.materials.append(mat)
 return ob

def material(name,col,metal,rough):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True
 bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 return m
silver=material('Silver — appearance from 373_377',(.72,.75,.78),1,.16)
black=material('Black — appearance from 377',(.013,.016,.021),.25,.29)
gun=material('Gunmetal — appearance from 377',(.105,.115,.132),.8,.26)
face=material('Textured black panel',(.024,.028,.031),.12,.39)
red=material('Red outward pull knob',(.82,.018,.003),0,.29)
white=material('White protective cap — thread hidden',(.8,.84,.88),0,.35)
clay=material('Inspection gray',(.43,.46,.49),0,.5)
# Native procedural grain, independent of photographed lighting.
nt=face.node_tree;n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=5200;n.inputs['Roughness'].default_value=.7
b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.22;b.inputs['Distance'].default_value=.000045
nt.links.new(n.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs['Normal'],next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED').inputs['Normal'])

def rr(w,h,r,z,n=24):
 pts=[]
 for cx,cy,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
  for i in range(n):
   a=math.radians(start+i*90/(n-1));pts.append((cx+r*math.cos(a),cy+r*math.sin(a),z))
 return pts

def profile_rr(name,profiles,mat,cap_first=False,cap_last=False):
 vs=[];fs=[];N=96
 for pr in profiles:vs+=rr(*pr)
 for j in range(len(profiles)-1):
  for i in range(N):k=j*N+i;l=j*N+(i+1)%N;fs.append((k,l,l+N,k+N))
 if cap_first:fs.append(tuple(range(N-1,-1,-1)))
 if cap_last:fs.append(tuple(range((len(profiles)-1)*N,len(profiles)*N)))
 ob=mesh(name,vs,fs,mat)
 for f in ob.data.polygons:f.use_smooth=len(f.vertices)==4
 return ob
# Actual enclosed shell, open front cavity; internal 2 mm wall is an editable visualization estimate.
shell=profile_rr('Housing_300x200x20',[(297,197,20,-10),(299.2,199.2,21.1,-9.6),(300,200,21.5,-8.5),(300,200,21.5,8.5),(299.4,199.4,21.2,9.5),(298.5,198.5,20.75,10),(296.2,196.2,19.6,9.7),(295.5,195.5,19.25,8.9),(295.5,195.5,19.25,-7.7)],silver,True,True)
panel=profile_rr('Recessed_panel_with_true_through_holes',[(294.8,194.8,19,4.7),(294.8,194.8,19,8.85),(293.8,193.8,18.5,8.7),(291.3,191.3,17.3,8.15),(287,187,15.2,7.35),(282,182,13,7.2)],face,True,True)
# Each H is manually identified from 372 circle-contact and checked against 376.
# No inferred holes in repeated decorative cells. Center 08/06 is occluded by the knob.
H=[list(range(13)),[0,13],[1,3,5,7,9,11],[0,2,6,11,13],[0,2,4,6,8,10,12],[0,4,9,13],[1,3,5,7,9,11],[0,13],[0,2,4,8,10,12],[0,13],[1,3,5,7,9,11],[0,4,9,13],[0,2,4,6,8,10,12],[0,2,6,11,13],[1,3,5,7,9,11],[0,13],list(range(13))]
rows=[];pitch=20.2
for r in range(17):
 for c in range(14 if r%2 else 13):
  x=(c-(6.5 if r%2 else 6))*pitch;y=(8-r)*pitch/2
  kind='HOLE' if c in H[r] else ('OCCLUDED_KNOB' if (r,c)==(8,6) else 'BLIND_DOT')
  rows.append(dict(id=f'R{r:02}C{c:02}',row=r,col=c,x_mm=x,y_mm=y,kind=kind,source='372; visible cross-check 376',photo_rect_x=(102 if r%2 else 165)+c*123,photo_rect_y=105+r*60.7))
assert sum(a['kind']=='HOLE' for a in rows)==96
with (P/'hole-map.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
# Single Boolean operand: all shallow circles / petal reliefs, then separately the genuine bores.
cv=[];cf=[]
def prism(poly,z0,z1):
 off=len(cv);N=len(poly);cv.extend([(x,y,z0) for x,y in poly]+[(x,y,z1) for x,y in poly]);cf.extend([tuple(off+i for i in range(N-1,-1,-1)),tuple(off+N+i for i in range(N))])
 for i in range(N):j=(i+1)%N;cf.append((off+i,off+j,off+N+j,off+N+i))
def circ(x,y,r,z0,z1,n=32):prism([(x+r*math.cos(i*2*math.pi/n),y+r*math.sin(i*2*math.pi/n)) for i in range(n)],z0,z1)
for a in rows:
 if a['kind']!='OCCLUDED_KNOB':circ(a['x_mm'],a['y_mm'],2.12,6.97,7.6)
# Lens reliefs: shared between adjacent decorative cells; all are closed recessed geometry.
lenses={}
for a in rows:
 for sx in [-1,1]:
  for sy in [-1,1]:
   x=a['x_mm']+sx*pitch/4;y=a['y_mm']+sy*pitch/4
   if abs(x)>138 or abs(y)>88:continue
   angle=-sx*sy*math.pi/4;lenses[(round(x,3),round(y,3))]=(x,y,angle)
for x,y,a in lenses.values():
 poly=[]
 for i in range(32):
  t=2*math.pi*i/32;u=6.7*math.cos(t);v=1.95*math.sin(t)*abs(math.sin(t))**.35
  poly.append((x+u*math.cos(a)-v*math.sin(a),y+u*math.sin(a)+v*math.cos(a)))
 prism(poly,6.97,7.65)

def subtract(name):
 global cv,cf
 cutter=mesh(name,cv,cf);bpy.context.view_layer.objects.active=panel
 mod=panel.modifiers.new(name,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True);cv=[];cf=[]
subtract('Shallow_petals_and_blind_dot_recesses')
for a in rows:
 if a['kind']=='HOLE':circ(a['x_mm'],a['y_mm'],.57,4,8,32)
# central shaft aperture is an assembly opening, not a water outlet.
circ(0,0,3.1,4,10,48)
subtract('96_verified_outlet_bores_and_shaft_aperture')
# Small deterministic edge radius keeps the stamped relief from razor-sharp black artifacts.
bev=panel.modifiers.new('Relief_edge_softness_estimated_0.06mm','BEVEL');bev.width=.00006;bev.segments=2
# lathed editable external parts

def lathe(name,profile,mat,N=96):
 vs=[];fs=[]
 for r,z in profile:
  for i in range(N):t=2*math.pi*i/N;vs.append((max(r,.0001)*math.cos(t),max(r,.0001)*math.sin(t),z))
 for j in range(len(profile)-1):
  for i in range(N):k=j*N+i;l=j*N+(i+1)%N;fs.append((k,l,l+N,k+N))
 fs.extend([tuple(range(N-1,-1,-1)),tuple(range((len(profile)-1)*N,len(profile)*N))])
 ob=mesh(name,vs,fs,mat)
 for p in ob.data.polygons:p.use_smooth=len(p.vertices)==4
 return ob
knob=lathe('Outward_pull_knob_concave_face',[(0,12.05),(5,12.05),(9.5,12.5),(11.6,13.2),(12.3,13.6),(12.7,13.35),(12.7,12),(12.1,10.8),(10.4,10),(3,9.2),(3,5),(0,5)],red)
conn=lathe('Rear_connector_visible_envelope_UNCONFIRMED_thread',[(0,-10),(20.5,-10),(21,-10.8),(21,-12),(19.8,-13),(18.8,-13.5),(18.8,-15),(17,-15.8),(15.4,-16),(15.4,-28.5),(14.8,-30),(12,-30),(12,-40),(0,-40)],silver)
cap=lathe('Observed_white_protective_cap',[(0,-40),(11.9,-40),(12.2,-40.5),(12.2,-42),(11.6,-42.4),(0,-42.4)],white)
for ob in [shell,panel,knob,conn,cap]:ob['source']='products/长方形拉钮顶喷/原始实拍20261030; see README';ob['precision']='Appearance reconstruction, not manufacturing CAD'
knob['operation']='PULL OUTWARD +Z; stroke UNKNOWN; no animation'
conn['thread_spec']='UNKNOWN; not modeled under protective cap'
# Inspection of real panel geometry before display modifiers.
bm=bmesh.new();bm.from_mesh(panel.data)
meshcheck={'panel_vertices':len(bm.verts),'panel_faces':len(bm.faces),'panel_nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'panel_degenerate_faces':sum(f.calc_area()<1e-14 for f in bm.faces)};bm.free()
hits=[]
for a in rows:
 if a['kind']=='HOLE':
  # Stop at panel underside: back housing is an intentional cavity boundary, not a plugged bore.
  ok,loc,n,idx=panel.ray_cast(Vector((a['x_mm']*.001,a['y_mm']*.001,.0085)),Vector((0,0,-1)),distance=.0042)
  hits.append({'id':a['id'],'blocked_by_panel':bool(ok)})
meshcheck['bore_axis_checks']=hits;meshcheck['all_96_bore_axes_open']=not any(a['blocked_by_panel'] for a in hits)
meshcheck['housing_mm']=[round(v*1000,5) for v in shell.dimensions]
meshcheck['known_holes']=96;meshcheck['blind_dots']=sum(a['kind']=='BLIND_DOT' for a in rows);meshcheck['occluded_cells']=1
meshcheck['petal_reliefs']=len(lenses)
(P/'geometry-check.json').write_text(json.dumps(meshcheck,indent=2))
assert meshcheck['all_96_bore_axes_open'], 'A verified bore is plugged'
assert meshcheck['panel_nonmanifold_edges']==0,'Panel is not manifold'
assert all(abs(a-b)<.01 for a,b in zip(meshcheck['housing_mm'],[300,200,20]))
# Cameras, lights and consistent neutral inspection environment.
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1400;scene.render.resolution_y=1050;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=95
scene.world.color=(.28,.28,.28);scene.view_settings.view_transform='AgX'
world=scene.world;world.use_nodes=True;next(n for n in world.node_tree.nodes if n.type=='BACKGROUND').inputs[0].default_value=(.36,.39,.43,1);next(n for n in world.node_tree.nodes if n.type=='BACKGROUND').inputs[1].default_value=.5

def aim(ob,target):ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
def light(name,loc,power,size):
 da=bpy.data.lights.new(name,'AREA');da.energy=power;da.shape='DISK';da.size=size;ob=bpy.data.objects.new(name,da);scene.collection.objects.link(ob);ob.location=loc;aim(ob,(0,0,0))
light('Large softbox',(-.18,.22,.35),35,.28);light('Strip reflection',(.25,.07,.2),20,.16);light('Back softbox',(-.15,.1,-.3),40,.3);light('Lower edge fill',(0,-.3,.12),12,.2)
def camera(name,loc,scale=.38,target=(0,0,0)):
 ca=bpy.data.cameras.new(name);ca.type='ORTHO';ca.ortho_scale=scale;ob=bpy.data.objects.new(name,ca);scene.collection.objects.link(ob);ob.location=loc;aim(ob,target);ca.clip_start=.001;return ob
cams={
 '01_gray_front':camera('Front orthographic',(0,0,.6)),
 '02_gray_back':camera('Back orthographic',(0,0,-.6)),
 '03_gray_long_side':camera('Long side',(0,-.6,0)),
 '04_gray_short_side':camera('Short side',(.6,0,0)),
 '05_gray_oblique':camera('Front oblique',(.30,-.37,.48)),
 '06_silver_front':camera('Silver front oblique',(.21,-.30,.55)),
 '07_silver_back':camera('Silver back oblique',(.22,-.30,-.55)),
 '08_black_back':camera('Black back oblique',(.22,-.30,-.55)),
 '09_gunmetal_back':camera('Gunmetal back oblique',(.22,-.30,-.55)),
 '10_panel_detail':camera('True holes vs blind dots',(-.12,.06,.25),.085,(-.075,.035,.007))}
parts=[shell,panel,knob,conn,cap];original=[o.data.materials[0] for o in parts]
scene.camera=cams['06_silver_front']
for ob in parts:ob.select_set(True)
bpy.context.view_layer.objects.active=shell
bpy.ops.wm.save_as_mainfile(filepath=str(P/'长方形拉钮顶喷_v1.blend'))
for key,cam in cams.items():
 for ob,ma in zip(parts,original):ob.data.materials[0]=clay if 'gray' in key else ma
 if 'black' in key:shell.data.materials[0]=conn.data.materials[0]=black
 if 'gunmetal' in key:shell.data.materials[0]=conn.data.materials[0]=gun
 scene.camera=cam;scene.render.filepath=str(P/(key+'.jpg'));bpy.ops.render.render(write_still=True)
print('BUILD_AND_RENDER_FINISHED',flush=True)
