"""Render the downloaded trial in a new scene. Never opens the protected model."""
from pathlib import Path
import json
import bpy
from mathutils import Vector

OUT = Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(OUT / "round-shower-tripo-h25-single.glb"))
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
points = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
lo = Vector(tuple(min(p[i] for p in points) for i in range(3)))
hi = Vector(tuple(max(p[i] for p in points) for i in range(3)))
center = (lo + hi) / 2
scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.render.resolution_x = 900
scene.render.resolution_y = 600
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.display.shading.light = "STUDIO"
scene.display.shading.studiolight_rotate_z = 0.3
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = "BOTH"
scene.display.shading.background_type = "WORLD"
scene.world = bpy.data.worlds.new("TrialReviewWorld")
scene.world.color = (0.12, 0.12, 0.12)
scene.view_settings.view_transform = "Standard"
camdata = bpy.data.cameras.new("TrialReviewCamera")
cam = bpy.data.objects.new("TrialReviewCamera", camdata)
scene.collection.objects.link(cam)
scene.camera = cam
camdata.type = "ORTHO"
camdata.ortho_scale = max(hi - lo) * 1.12

views = [
    ("front-texture", (0, -3, 0), "TEXTURE"),
    ("back-texture", (0, 3, 0), "TEXTURE"),
    ("side-geometry", (0, 0.02, 3), "MATERIAL"),
    ("front-geometry", (0, -3, 0), "MATERIAL"),
    ("back-oblique", (0.65, 2.4, 1.0), "TEXTURE"),
    ("front-oblique", (0.65, -2.4, 1.0), "TEXTURE"),
]
for o in meshes:
    o.color = (0.55, 0.55, 0.55, 1)
for name, offset, mode in views:
    cam.location = center + Vector(offset)
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.display.shading.color_type = mode
    if mode == "MATERIAL":
        scene.display.shading.color_type = "OBJECT"
    scene.render.filepath = str(OUT / (name + ".png"))
    bpy.ops.render.render(write_still=True)

stats = {
    "source": "round-shower-tripo-h25-single.glb",
    "view_method": "New Blender scene, orthographic workbench renders; no repair or smoothing applied.",
    "mesh_count": len(meshes),
    "vertices": sum(len(o.data.vertices) for o in meshes),
    "polygons": sum(len(o.data.polygons) for o in meshes),
    "bounds_min": list(lo), "bounds_max": list(hi),
    "bounds_dimensions_arbitrary_units": list(hi - lo),
    "physical_dimensions_verified": False,
    "renders": [name + ".png" for name, _, _ in views],
}
(OUT / "mesh-review.json").write_text(json.dumps(stats, indent=2) + "\n")
print("TRIAL_REVIEW_RENDERED", json.dumps(stats))
