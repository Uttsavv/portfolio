"""Experience scene: a stackable slab (the site stacks it per year of work) and a flag."""
import math
from lib import *  # noqa: F401,F403
from lib import MATS


def slab(name, mat, edge):
    """2.3 x 2.3 x 0.4 rounded slab with a groove around its waist so stacked slabs read as layers."""
    s = box(name, (2.3, 2.3, 0.4), (0, 0, 0.2), mat)
    bevel_mod(s, 0.07, 4, 30)
    for k in range(4):
        g = box(name + "g", (2.5, 0.03, 0.035), (0, 0, 0.2), None)
        g.rotation_euler = (0, 0, k * math.pi / 2)
        g.location = (0, 0, 0)
        g.data.transform(Matrix.Translation((0, 1.15, 0)))
        apply_transform(g)
        boolean(s, g)
    parts = [s, box(name + "lip", (2.18, 2.18, 0.02), (0, 0, 0.405), edge, 0.008)]
    o = join(name, parts)
    return shade(o, 35)


def flag():
    steel, glow = MATS["steel"], MATS["glow"]
    parts = [
        cylinder("pole", 0.028, 1.6, (0, 0, 0), 16, steel),
        sphere("knob", 0.055, (0, 0, 1.62), 16, 8, steel),
        cylinder("foot", 0.12, 0.05, (0, 0, 0), 24, steel, r2=0.09, bevel=0.01),
    ]
    pole = shade(join("flagPole", parts), 40)
    # flag cloth: a subdivided plane (the site waves its vertices)
    bm = bmesh.new()
    cols, rows = 16, 6
    v = [[bm.verts.new((-0.92 * i / cols, 0, 1.02 + 0.56 * j / rows)) for j in range(rows + 1)] for i in range(cols + 1)]
    for i in range(cols):
        for j in range(rows):
            bm.faces.new((v[i][j], v[i + 1][j], v[i + 1][j + 1], v[i][j + 1]))
    cloth = mesh_obj("flagCloth", bm, glow)
    for p in cloth.data.polygons:
        p.use_smooth = True
    return [pole, cloth]


def block(name, mat, top):
    """A tall smooth block; the site sinks it into the floor so only its rounded top part shows."""
    b = box(name, (2.3, 2.3, 6.0), (0, 0, -3.0 + 0.0), mat)
    bevel_mod(b, 0.24, 8, 30)
    o = join(name, [b])
    return shade(o, 40)


def build(coll):
    objs = [block("block", MATS["clay"], None), block("blockNow", MATS["blue"], None)]
    objs[0].location = (-3, 0, 0)
    objs[1].location = (0, 0, 0)
    objs += flag()
    for o in objs[2:]:
        o.location = (6, 0, 0)
    for o in objs:
        for c in o.users_collection:
            c.objects.unlink(o)
        coll.objects.link(o)
    return objs
