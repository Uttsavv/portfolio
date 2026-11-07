"""Contact scene: envelope with a hinged flap, a letter, a wax seal and a paper plane."""
import math
from lib import *  # noqa: F401,F403
from lib import MATS


def M(n):
    return MATS[n]


def flat(name, pts2d, z0, t, mat, bevel=0.0):
    o = prism_xy(name, pts2d, z0, z0 + t, mat)
    if bevel:
        bevel_mod(o, bevel, 2, 30)
    return o


def envelope():
    paper, shade_m, glow, ink = M("paper"), M("paperShade"), M("glow"), M("ink")
    W, D = 3.4, 2.3  # x by y (y = depth; +y is the back, where the flap hinges)
    body = flat("env_back", [(-W / 2, -D / 2), (W / 2, -D / 2), (W / 2, D / 2), (-W / 2, D / 2)], 0, 0.06, shade_m, 0.012)
    parts = [body]
    # inner pocket walls so it reads as an open envelope
    for s in (-1, 1):
        parts.append(box("env_side", (0.02, D - 0.04, 0.12), (s * (W / 2 - 0.01), 0, 0.12), paper))
    # front panels: bottom triangle and two side triangles, slightly raised, like folded paper
    parts.append(flat("env_left", [(-W / 2, -D / 2), (-W / 2, D / 2), (-0.25, 0.05)], 0.19, 0.012, paper, 0.004))
    parts.append(flat("env_right", [(W / 2, D / 2), (W / 2, -D / 2), (0.25, 0.05)], 0.19, 0.012, paper, 0.004))
    parts.append(flat("env_bottom", [(-W / 2, -D / 2), (W / 2, -D / 2), (0, 0.2)], 0.2, 0.012, paper, 0.004))
    parts.append(box("env_filler", (W - 0.04, D - 0.04, 0.13), (0, 0, 0.125), shade_m))
    o = shade(join("envelope", parts), 30)
    # flap: separate, origin on the hinge line (back edge, top), lying closed toward the front
    fl = [flat("flap_p", [(-W / 2, 0), (0, -1.35), (W / 2, 0)], 0, 0.012, paper, 0.004)]
    seal = cylinder("seal", 0.17, 0.04, (0, -1.15, 0.012), 40, glow, bevel=0.015)
    fl.append(seal)
    u = text_mesh("seal_u", "U", 0.17, 0.006, M("blue"))
    u.location = (0, -1.15, 0.055)
    apply_transform(u)
    fl.append(u)
    flap = shade(join("flap", fl), 30)
    flap.location = (0, D / 2, 0.205)
    return o, flap


def letter():
    paper, ink, glow, clay2 = M("paper"), M("ink"), M("glow"), M("clay2")
    W, H = 2.85, 1.9
    p = [box("lt_sheet", (W, 0.025, H), (0, 0, 0), paper, 0.006)]
    # handwritten-ish lines on the front (-Y)
    rows = [(0.62, 0.7, ink), (0.38, 2.2, clay2), (0.18, 2.0, clay2), (-0.02, 2.3, clay2), (-0.22, 1.5, clay2), (-0.55, 0.6, ink)]
    for z, w, m in rows:
        p.append(box("lt_line", (w, 0.01, 0.06), (-W / 2 + 0.25 + w / 2, -0.016, z), m))
    p.append(box("lt_stamp", (0.34, 0.012, 0.4), (W / 2 - 0.35, -0.016, 0.58), glow, 0.01))
    return shade(join("letter", p), 30)


def paper_plane():
    """Classic dart: two wings and a keel, folded paper with a little thickness. Nose points +Y."""
    paper, shade_m = M("paper"), M("paperShade")
    L, S = 1.2, 0.95
    nose = (0, L, 0)
    tail_c = (0, -0.6, 0)
    keel = (0, -0.55, -0.32)
    wl, wr = (-S, -0.62, 0.08), (S, -0.62, 0.08)
    fold_l, fold_r = (-0.12, -0.6, 0.0), (0.12, -0.6, 0.0)
    bm = bmesh.new()

    def tri(a, b, c, mat_i):
        vs = [bm.verts.new(a), bm.verts.new(b), bm.verts.new(c)]
        f = bm.faces.new(vs)
        f.material_index = mat_i

    tri(nose, wl, fold_l, 0)
    tri(nose, fold_l, tail_c, 1)
    tri(nose, fold_r, wr, 0)
    tri(nose, tail_c, fold_r, 1)
    tri(nose, keel, tail_c, 1)
    tri(nose, tail_c, keel, 1)
    o = mesh_obj("plane", bm)
    o.data.materials.append(paper)
    o.data.materials.append(shade_m)
    solidify(o, 0.012, 0)
    return shade(o, 20)


def build(coll):
    env, flap = envelope()
    lt = letter()
    lt.location = (0, 0.2, 0.2)
    pl = paper_plane()
    pl.location = (4, 0, 1)
    objs = [env, flap, lt, pl]
    for o in objs:
        for c in o.users_collection:
            c.objects.unlink(o)
        coll.objects.link(o)
    return objs
