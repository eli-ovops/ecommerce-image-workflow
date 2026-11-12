# Executed before rigid placement: geometric openings, not painted dots.
import bmesh
panel=bpy.data.objects['02 Continuous black face and selector surround']
positions=json.loads((SRC.parent/'white-hole-layout.json').read_text())['positions_row_x_v_mm']
def fy(z):
 if z>=155:return (5+(210-z)*.1)*.001
 t=max(0,min(1,(z-110)/45));return ((2*t**3-3*t*t+1)*7+(t**3-2*t*t+t)*3.6+(-2*t**3+3*t*t)*10.5+(t**3-t*t)*(-4.5))*.001
vs=[];fs=[]
def cutter(x,z,r,N=20):
 k=len(vs);y=fy(z)
 for d in [-.006,.006]:
  for i in range(N):
   a=i*math.tau/N;vs.append((x*.001+r*math.cos(a),y+d,z*.001+r*math.sin(a)))
 for i in range(N):j=(i+1)%N;fs.append((k+i,k+j,k+N+j,k+N+i))
 fs.append(tuple(k+i for i in reversed(range(N))));fs.append(tuple(k+N+i for i in range(N)))
for row,x,v in positions:cutter(x,210+v/math.sqrt(1.01),.00185)
for r in [56,58.6,61]:
 for i in range(100):
  a=i*math.tau/100;cutter(r*math.cos(a),210+r*math.sin(a)/math.sqrt(1.01),.00059,12)
me=bpy.data.meshes.new('All opening cutters');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();cut=bpy.data.objects.new('Hidden editable hole cutters',me);S.collection.objects.link(cut)
mod=panel.modifiers.new('Actual recessed openings','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
bpy.context.view_layer.objects.active=panel
# Apply only on the new validation copy for stable reopening and rendering.
bpy.ops.object.modifier_apply(modifier='Insert thickness');bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(cut,do_unlink=True)
for v in bpy.data.objects['03 White nozzles - 144 mapped positions'].data.vertices:v.co.y+=.00065
for v in bpy.data.objects['04 Nozzle dark recesses'].data.vertices:v.co.y-=.0001
old=bpy.data.objects['05 Peripheral micro hole mouths - simplified 3 x 100'];old.hide_render=True;old.hide_viewport=True
# Black backing surface sits behind the apertures, above exterior shell.
back=panel.copy();back.data=panel.data.copy();back.name='10 Dark recessed backing';S.collection.objects.link(back)
# A continuous backing from original panel mesh, avoiding expensive shell cuts.
bpy.data.objects.remove(back,do_unlink=True)
# Thin black face-sized disk at y just ahead of shell; top surface follows head plane.
verts=[];faces=[]
for j in range(129):
 z=147+126*j/128;w=math.sqrt(max(0,63**2-(z-210)**2))
 for i in range(65):verts.append((w*(2*i/64-1)*.001,fy(z)-.00012,z*.001))
for j in range(128):
 for i in range(64):
  k=j*65+i;faces.append((k,k+1,k+66,k+65))
me=bpy.data.meshes.new('Recess backing');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new('10 Dark aperture backing',me);S.collection.objects.link(ob);ob.data.materials.append(dark);product.append(ob)
