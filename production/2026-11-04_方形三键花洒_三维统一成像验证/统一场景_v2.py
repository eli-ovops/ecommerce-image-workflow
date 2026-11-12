import bpy, math, json
from mathutils import Vector
from pathlib import Path
p=Path('/Volumes/EXTERNAL/电商 作图工作流/production/2026-11-04_方形三键花洒_三维统一成像验证')
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for m in bpy.data.materials: bpy.data.materials.remove(m)
def material(name,color,metal=0,rough=.4):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;n=next(v for v in m.node_tree.nodes if v.type=='BSDF_PRINCIPLED');n.inputs['Base Color'].default_value=(*color,1);n.inputs['Metallic'].default_value=metal;n.inputs['Roughness'].default_value=rough;return m
chrome=material('银色金属',(.65,.68,.70),1,.16);dark=material('深色微纹喷面',(.028,.031,.032),.02,.48);rubber=material('白色硅胶嘴',(.87,.86,.81),0,.39);black=material('黑色喷嘴',(.014,.015,.014),0,.39);button=material('三枚黑色按键',(.019,.022,.023),.02,.42);emboss=material('按键标记凹痕',(.058,.062,.062),.03,.42);gold=material('背景暖米金',(.56,.39,.26),0,.5);floor=material('浅米色台面',(.59,.46,.35),.12,.3)
# 面板与外壳的轮廓只依照片比例估建，深度为视觉估计。
def roundbox(name,loc,scale,mat,bevel=.1):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);be=o.modifiers.new('圆角','BEVEL');be.width=bevel;be.segments=6;o.modifiers.new('平滑法线','WEIGHTED_NORMAL');o.data.materials.append(mat);return o
head=roundbox('圆角长方形银色喷头外壳',(0,.13,4.52),(2.81,.54,3.17),chrome,.25)
# 前表面网格，中心比边缘退后：y正方向远离正面观察者。
zc=4.52; a=1.31; b=1.50
N=128; R=25; verts=[];faces=[]
for ri in range(R+1):
 r=max(.0001,ri/R)
 for j in range(N):
  t=2*math.pi*j/N; cs=math.cos(t);sn=math.sin(t);x=a*r*math.copysign(abs(cs)**.42,cs);z=zc+b*r*math.copysign(abs(sn)**.42,sn);y=-.22+.12*(1-r**4);verts.append((x,y,z))
for i in range(R):
 for j in range(N):
  j2=(j+1)%N;faces.append((i*N+j,i*N+j2,(i+1)*N+j2,(i+1)*N+j))
mesh=bpy.data.meshes.new('凹面网格');mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new('真实照片引导的浅凹面',mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(dark)
for f in mesh.polygons:f.use_smooth=True
def panel_y(x,z):
 r=min(1,((abs(x)/a)**4.76+(abs(z-zc)/b)**4.76)**(1/4.76));return -.22+.12*(1-r**4)
def nozzle(name,x,z,kind):
 y=panel_y(x,z)-.019
 if kind=='heart':
  verts=[];faces=[]; n=60
  for depth in [0,.025]:
   for i in range(n):
    t=2*math.pi*i/n; xx=16*math.sin(t)**3/17; zz=(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))/17
    verts.append((x+xx*.122,y-depth,z+zz*.122))
  faces.append(tuple(range(n-1,-1,-1)));faces.append(tuple(range(n,2*n)))
  for i in range(n): j=(i+1)%n;faces.append((i,j,j+n,i+n))
  me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(rubber);be=o.modifiers.new('柔和边缘','BEVEL');be.width=.009;be.segments=3;o.modifiers.new('法线','WEIGHTED_NORMAL');r=.008
 else:
  r0=.053 if kind=='round' else .066;bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r0,depth=.025,location=(x,y-.01,z),rotation=(math.pi/2,0,0));o=bpy.context.object;o.name=name;o.data.materials.append(rubber if kind=='round' else black);be=o.modifiers.new('喷嘴圆角','BEVEL');be.width=.008;be.segments=3;o.modifiers.new('法线','WEIGHTED_NORMAL');r=.009 if kind=='round' else .014
 bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=.002,location=(x,y-.025,z),rotation=(math.pi/2,0,0));bpy.context.object.data.materials.append(black)
items=json.loads((p/'465_白嘴提取.json').read_text())['items']
for i,v in enumerate(items):
 x=(600-v['source_y'])/210;z=3.10+(740-v['source_x'])/210
 nozzle('实拍位置白嘴_%02d'%i,x,z,v['kind'])
for y in [465,600,730]:
 for x in [351,550]:nozzle('黑色喷嘴',(600-y)/210,3.10+(740-x)/210,'black')
# 头颈银色轮廓与内层面板一体：曲线多边形；不使用实拍像素。
def plate(name,coords,yy,mat,extrude):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='2D';cu.fill_mode='BOTH';cu.resolution_u=20;cu.extrude=extrude;cu.bevel_depth=.025;cu.bevel_resolution=4;s=cu.splines.new('BEZIER');s.bezier_points.add(len(coords)-1)
 for bp,(x,z) in zip(s.bezier_points,coords):bp.co=(x,z,0);bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
 s.use_cyclic_u=True;s.bezier_points[0].handle_left_type='VECTOR';s.bezier_points[-1].handle_right_type='VECTOR';o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o);o.rotation_euler=(math.pi/2,0,0);o.location.y=yy;o.data.materials.append(mat);return o
plate('银色头颈',[(-1.19,3.15),(-.94,2.85),(-.52,2.45),(-.41,1.48),(.41,1.48),(.52,2.45),(.94,2.85),(1.19,3.15)],.12,chrome,.21)
plate('黑色三键底座',[(-1.05,3.14),(-.83,2.86),(-.48,2.46),(-.37,1.55),(.37,1.55),(.48,2.46),(.83,2.86),(1.05,3.14)],-.25,dark,.055)
roundbox('银色手柄',(0,.01,.81),(.82,.48,2.03),chrome,.10)
# 三键按实拍左右及上下位置排布，图案为可辨示意而非工业刻纹。
roundbox('左上喷雾键',(-.30,-.37,2.61),(.56,.08,.40),button,.075)
roundbox('右上花洒键',(.30,-.37,2.61),(.56,.08,.40),button,.075)
roundbox('下方喷枪键',(0,-.37,2.04),(.60,.08,.43),button,.08)
def line(name,points,r=.009,mat=emboss):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=8;cu.bevel_depth=r;cu.bevel_resolution=2;s=cu.splines.new('POLY');s.points.add(len(points)-1)
 for q,pt in zip(s.points,points):q.co=(*pt,1)
 o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o);o.data.materials.append(mat)
for cx in [-.30,.30]: line('按键顶部横杠',[(cx-.13,-.423,2.70),(cx+.13,-.423,2.70)],.013)
for col in range(5):
 for row in range(3):
  dx=(col-2)*.047
  # 左为外扩，右为直线
  for cx in [-.30,.30]:
   dz=2.65-row*.05;offset=dx*(1+row*.10) if cx<0 else dx
   line('水型图案',[(cx+offset,-.424,dz),(cx+offset+(dx*.10 if cx<0 else 0),-.424,dz-.025)],.008)
line('喷枪横杠',[(-.14,-.423,2.15),(.14,-.423,2.15)],.014);line('喷枪竖线',[(0,-.423,2.10),(0,-.423,1.98)],.014)
# 同一场景中的环境与光线。
roundbox('背景墙',(0,2.0,3.4),(18,.18,10),gold,.1);roundbox('浴室台面',(0,0,-.44),(18,12,.35),floor,.1)
def area(name,loc,energy,size,color,target):
 data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size;data.color=color;o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('左侧暖大窗',(-5,-5,8),750,5,(1,.82,.65),(0,0,3));area('右侧柔光',(5,-3,6),950,4,(1,.92,.82),(0,0,3));area('顶部柔光',(0,0,10),800,4,(1,.86,.70),(0,0,2))
bpy.context.scene.world.color=(.34,.29,.25)
data=bpy.data.cameras.new('camera');cam=bpy.data.objects.new('camera',data);bpy.context.collection.objects.link(cam);cam.location=(.15,-13.0,4.1);cam.rotation_euler=(Vector((0,0,3.1))-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=7.5;bpy.context.scene.camera=cam
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.render.resolution_x=1400;scene.render.resolution_y=1400;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(p/'三维统一成像_结构验证_v2.png');bpy.ops.wm.save_as_mainfile(filepath=str(p/'方形三键_结构估建场景_v2.blend'));bpy.ops.render.render(write_still=True)
