import bpy,json,hashlib,struct
from pathlib import Path
P=Path(__file__).resolve().parent;S=P.parent/'2026-10-31_顶喷孔位回源可控修复'
def fingerprint(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(struct.pack('3d',*v.co))
 for f in o.data.polygons:h.update(str(tuple(f.vertices)).encode())
 return h.hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(S/'399-preview.blend'));original=fingerprint(bpy.data.objects['Housing_300x200x20'])
bpy.ops.wm.open_mainfile(filepath=str(P/'391-installation.blend'));shell=bpy.data.objects['Housing_300x200x20'];face=bpy.data.objects['ONLY_PHOTO_FACE_NO_DUPLICATE_CIRCLES'];water=[o for o in bpy.data.objects if o.name.startswith('WATER_')]
checks={'shell_vertices_topology_unchanged':original==fingerprint(shell),'single_photo_face_polygon':len(face.data.polygons)==1,'old_perforated_panel_absent':'Recessed_panel_with_true_through_holes' not in bpy.data.objects,'94_independent_water_curve_objects':len(water)==94,'uncertain2_outlets_absent':not any(o.name in ['WATER_R03C06','WATER_R13C06'] for o in water),'photo_texture_packed':all(n.image.packed_file is not None for n in face.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE')}
(P/'blend-check.json').write_text(json.dumps({'checks':checks,'shell_hash':fingerprint(shell),'source_shell_hash':original,'limitations':'Checks do not validate actual installed connector, real water flow, photographic realism or factory hole count.'},indent=2));print(checks);assert all(checks.values())
