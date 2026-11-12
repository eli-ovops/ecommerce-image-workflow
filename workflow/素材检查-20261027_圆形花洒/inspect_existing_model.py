"""Render unchanged v010a geometry for comparison with the new silver photos."""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path('/Volumes/EXTERNAL/电商 作图工作流')
SOURCE = ROOT / 'production/2026-10-24_实物建模/blender/v010a/shower_black_clay_v010a.blend'
OUT = ROOT / 'production/2026-10-27_圆形花洒_形状基准'
(OUT / '旧模型复核').mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.render.resolution_x = 800
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'JPEG'
scene.render.image_settings.quality = 94
scene.render.film_transparent = False
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'SINGLE'
scene.display.shading.single_color = (.55, .55, .55)
scene.display.shading.background_type = 'WORLD'
scene.world.color = (.85, .85, .85)
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = 'BOTH'
scene.display.shading.show_specular_highlight = False
cam = scene.camera
cam.data.type = 'ORTHO'
cam.data.ortho_scale = .31
target = Vector((0, .017, .1325))
meshes = []
for ob in scene.objects:
    if ob.type == 'MESH' and not ob.hide_render:
        meshes.append({'name': ob.name, 'dimensions_m': list(ob.dimensions), 'vertices': len(ob.data.vertices)})
views = [('front', 0, 0), ('back', 180, 0), ('right', 90, 0), ('left', -90, 0),
         ('front_oblique', 35, .10), ('back_oblique', 145, .10)]
for name, angle, elevation in views:
    a = math.radians(angle)
    cam.location = target + Vector((.7 * math.sin(a), -.7 * math.cos(a), elevation))
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = str(OUT / '旧模型复核' / (name + '.jpg'))
    bpy.ops.render.render(write_still=True)
(OUT / '旧模型复核' / 'runtime.json').write_text(json.dumps({
    'blender': bpy.app.version_string,
    'source': str(SOURCE), 'geometry_modified': False,
    'meshes': meshes, 'views': [x[0] for x in views],
    'status': 'REVIEW_REQUIRED_NEW_SILVER_PHOTOS',
    'limits': 'Historical auxiliary geometry only; no new metric fitting, nozzle completion, material or customer acceptance.'
}, ensure_ascii=False, indent=2))
print('UNCHANGED_MODEL_REVIEW_READY', OUT)
