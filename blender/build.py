"""Build every 3D scene of the portfolio and export one GLB per scene.

    pip install bpy==5.2.3        # Blender as a Python module
    python blender/build.py       # writes blender/out/*.glb
    npm run models                # compresses them into public/models/

Optional: python blender/build.py --preview  renders a Cycles still of each scene to blender/out/.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy  # noqa: E402
import math  # noqa: E402
from mathutils import Vector  # noqa: E402

import lib  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def materials():
    # Steel-blue clay family, one sky-blue glow. Names are read by the site's scene code.
    lib.material("clay", "#b9cde6", 0.5, 0.06)
    lib.material("clay2", "#7f98b8", 0.55, 0.06)
    lib.material("clayDark", "#5d7393", 0.55, 0.06)
    lib.material("marble", "#d9e5f3", 0.42, 0.04)
    lib.material("graphite", "#1b2131", 0.38, 0.35)
    lib.material("steel", "#8a95a8", 0.28, 0.85)
    lib.material("glow", "#5ab9fc", 0.4, 0.0, emit="#5ab9fc", emit_strength=1.6)
    lib.material("blue", "#2a6fb8", 0.35, 0.2)
    lib.material("glass", "#dfeaf7", 0.06, 0.0, transmission=1.0, ior=1.45)
    lib.material("paper", "#d6e4f5", 0.62, 0.0)
    lib.material("paperShade", "#a9bdd8", 0.6, 0.0)
    lib.material("ink", "#2a3346", 0.5, 0.0)
    lib.material("rubber", "#2b3447", 0.7, 0.0)


def export(coll, name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in coll.all_objects:
        o.select_set(True)
    os.makedirs(OUT, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, name + ".glb"),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_normals=True,
        export_texcoords=False,
        export_materials="EXPORT",
        export_extras=False,
        export_cameras=False,
        export_lights=False,
    )


def preview(coll, name, cam_loc, target, lens=40, size=(1200, 800)):
    sc = bpy.context.scene
    for c in sc.collection.children:
        c.hide_render = c is not coll
    cam = bpy.data.objects.get("pcam")
    if not cam:
        cam = bpy.data.objects.new("pcam", bpy.data.cameras.new("pcam"))
        sc.collection.objects.link(cam)
        sun = bpy.data.objects.new("psun", bpy.data.lights.new("psun", "SUN"))
        sun.data.energy = 3.5
        sun.rotation_euler = (math.radians(50), 0, math.radians(30))
        sc.collection.objects.link(sun)
        w = bpy.data.worlds.new("w")
        w.use_nodes = True
        w.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.025, 0.04, 1)
        w.node_tree.nodes["Background"].inputs[1].default_value = 1.2
        sc.world = w
    cam.data.lens = lens
    cam.location = cam_loc
    d = Vector(target) - Vector(cam_loc)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 24
    sc.cycles.device = "CPU"
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.filepath = os.path.join(OUT, "preview-" + name + ".png")
    bpy.ops.render.render(write_still=True)


def main():
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    do_preview = "--preview" in sys.argv
    lib.reset()
    materials()
    import delhi
    import career
    import projects
    import contact
    scenes = {
        "delhi": (delhi.build, ((4, -15, 4.5), (-0.5, 0, 2.4), 40)),
        "career": (career.build, ((3, -9, 4), (3, 0, 0.6), 40)),
        "projects": (projects.build, ((0, -16, 3), (0, 0, 0), 30)),
        "contact": (contact.build, ((2, -9, 6), (1.5, 0, 0.6), 35)),
    }
    for name, (fn, view) in scenes.items():
        if want and name not in want:
            continue
        coll = lib.collection(name)
        fn(coll)
        export(coll, name)
        if do_preview:
            preview(coll, name, *view)
        print("built", name, sum(len(o.data.polygons) for o in coll.all_objects if o.type == "MESH"), "faces")


if __name__ == "__main__":
    main()
