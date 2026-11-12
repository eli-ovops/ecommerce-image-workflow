import bpy,sys
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'05_浴室安装全貌.blend'))
s=bpy.context.scene;ma=bpy.data.materials['Bathroom limestone warm white']
# Replace overlapping Boolean/lining faces with four wall blocks and non-overlapping returns.
for o in list(bpy.data.objects):
 if o.name=='Limestone tiled shower wall' or o.name.startswith('Niche inner return') or o.name.startswith('Niche top return'):bpy.data.objects.remove(o,do_unlink=True)
def box(name,x0,x1,y0,y1,z0,z1):
 bpy.ops.mesh.primitive_cube_add(size=1,location=((x0+x1)/2,(y0+y1)/2,(z0+z1)/2));o=bpy.context.object;o.name=name;o.dimensions=(x1-x0,y1-y0,z1-z0);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma)
box('Wall left of niche',-1.2,-.31,.36,.44,0,3)
box('Wall right of niche',.01,1.2,.36,.44,0,3)
box('Wall above niche',-.31,.01,.36,.44,2.12,3)
box('Wall below niche',-.31,.01,.36,.44,0,1.68)
box('Niche left depth extension',-.318,-.31,.44,.51,1.68,2.12)
box('Niche right depth extension',.01,.018,.44,.51,1.68,2.12)
box('Niche top depth extension',-.318,.018,.44,.51,2.12,2.128)
preview='--preview' in sys.argv
s.cycles.samples=24 if preview else 128;s.render.resolution_percentage=50 if preview else 100
s.render.filepath=str(P/('05_浴室安装全貌_v2_preview.jpg' if preview else '05_浴室安装全貌_v2.jpg'))
if not preview:bpy.ops.wm.save_as_mainfile(filepath=str(P/'05_浴室安装全貌_v2.blend'))
bpy.ops.render.render(write_still=True)
