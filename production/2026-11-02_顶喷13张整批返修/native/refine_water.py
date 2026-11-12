import bpy,math,random,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent;S=P.parents[1]/'2026-11-02_391安装仰视单张实验'
bpy.ops.wm.open_mainfile(filepath=str(S/'391-installation.blend'));sc=bpy.context.scene;random.seed(1102)
old=[o for o in bpy.data.objects if o.name.startswith('WATER_')];water=old[0].data.materials[0];b=next(n for n in water.node_tree.nodes if n.type=='BSDF_PRINCIPLED');b.inputs['Roughness'].default_value=.04
records=[];drop_count=0
for ob in old:
 name=ob.name;start=Vector(ob.data.splines[0].bezier_points[0].co);end=Vector(ob.data.splines[0].bezier_points[-1].co);length=start.z-end.z;drift=end-start;phase=random.uniform(0,6.28)
 bpy.data.objects.remove(ob,do_unlink=True)
 cu=bpy.data.curves.new(name+'_varying_stream','CURVE');cu.dimensions='3D';cu.bevel_depth=.00042;cu.bevel_resolution=3;sp=cu.splines.new('POLY');sp.points.add(39)
 for i,pt in enumerate(sp.points):
  t=i/39;z=length*t;wob=(t*t)*.0013;pt.co=(*(start+Vector((drift.x*t+wob*math.sin(t*20+phase),drift.y*t+wob*math.cos(t*18+phase),-z))),1);pt.radius=max(.18,.8+.24*math.sin(t*43+phase)+.10*math.sin(t*77))
 neo=bpy.data.objects.new(name,cu);sc.collection.objects.link(neo);neo.data.materials.append(water)
 # Low-density droplets, independent geometry, no invented performance claim.
 for j in range(7):
  t=.28+j*.09+random.uniform(-.025,.025);pos=start+Vector((drift.x*t+random.uniform(-.0015,.0015),drift.y*t+random.uniform(-.0015,.0015),-length*t));r=random.uniform(.00065,.00115)
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=r,location=pos);d=bpy.context.object;d.name='DROP_'+name+'_'+str(j);d.scale=(.8,.8,random.uniform(1.1,1.9));d.data.materials.append(water)
  for f in d.data.polygons:f.use_smooth=True
  drop_count+=1
 records.append(dict(id=name,start=list(start),length=length))
sc.cycles.samples=64;sc.render.resolution_percentage=100;sc.render.filepath=str(P/'installed-refined.png');bpy.ops.wm.save_as_mainfile(filepath=str(P/'installed-refined.blend'));bpy.ops.render.render(write_still=True)
(P/'water-refinement.json').write_text(json.dumps(dict(source=str(S/'391-installation.blend'),origin_count=len(records),origins=records,droplets=drop_count,method='Native separate water curves with varying radii and sparse droplets; illustrative only, not CFD or measured flow',changed_product_geometry=False,excluded=['R03C06','R13C06']),indent=2))
