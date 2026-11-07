"""Project objects: handheld device, kanban board, glass jar, terminal window.
Each object is centred on its own origin; the site moves them through the carousel."""
import math
from lib import *  # noqa: F401,F403
from lib import MATS


def M(n):
    return MATS[n]


def rounded_rect(w, h, r, segs=6):
    pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for k in range(segs + 1):
            a = math.radians(a0 + 90 * k / segs)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def plate(name, w, h, d, r, mat, bevel=0.02, y=0.0):
    """Rounded-rectangle plate facing -Y (the camera), thickness d, front face at y."""
    p = prism(name, rounded_rect(w, h, r), y, y + d, mat)
    if bevel:
        bevel_mod(p, bevel, 3, 30)
    return p


# ------------------------------------------------------------ handheld

def handheld():
    clay, clay2, graphite, glow, steel, rubber = M("clay"), M("clay2"), M("graphite"), M("glow"), M("steel"), M("rubber")
    W, H, D = 1.4, 2.25, 0.3
    body = plate("hh_body", W, H, D, 0.16, clay, 0.05, -D / 2)
    # screen bezel recess and the speaker holes / button seats cut into the front
    boolean(body, plate("hh_cut", 1.16, 1.02, 0.06, 0.06, None, 0, -D / 2 - 0.02))
    for i in range(6):
        for j in range(4):
            c = cylinder("hh_hole", 0.016, 0.2, (0.3 + i * 0.05 - (j % 2) * 0.025, 0, -0.9 + j * 0.045), 8, None)
            c.rotation_euler = (math.pi / 2, 0, 0)
            c.location = (0.3 + i * 0.05 - (j % 2) * 0.025, -D / 2 + 0.05, -0.9 + j * 0.045)
            c.data.transform(Matrix.Translation((-c.location.x, 0, -c.location.z)))
            apply_transform(c)
            boolean(body, c)
    bevel_mod(body, 0.006, 1, 50)
    parts = [body]
    parts.append(plate("hh_bezel", 1.12, 0.98, 0.03, 0.05, graphite, 0.008, -D / 2 + 0.01))
    parts[-1].location = (0, 0, 0.47)
    apply_transform(parts[-1])
    scr = plate("screen", 0.9, 0.7, 0.01, 0.02, glow, 0, -D / 2 + 0.005)
    scr.location = (-0.0, 0, 0.47)
    apply_transform(scr)
    # D-pad
    dp = []
    dp.append(box("dpx", (0.36, 0.06, 0.11), (0, 0, 0), rubber))
    dp.append(box("dpy", (0.11, 0.06, 0.36), (0, 0, 0), rubber))
    pad = join("dpad", dp)
    bevel_mod(pad, 0.015, 2, 30)
    pad.location = (-0.33, -D / 2 - 0.02, -0.38)
    apply_transform(pad)
    parts.append(pad)
    # A/B buttons
    for x, z in ((0.42, -0.3), (0.22, -0.44)):
        b = cylinder("btn", 0.085, 0.07, (0, 0, 0), 28, glow if x > 0.3 else steel, bevel=0.02)
        b.rotation_euler = (math.pi / 2, 0, 0)
        b.location = (x, -D / 2 + 0.03, z)
        apply_transform(b)
        parts.append(b)
    # start / select pills
    for x in (-0.12, 0.12):
        pill = plate("pill", 0.18, 0.05, 0.03, 0.025, rubber, 0.008, 0)
        pill.rotation_euler = (0, math.radians(-25), 0)
        pill.location = (x, -D / 2 - 0.02, -0.7)
        apply_transform(pill)
        parts.append(pill)
    # shoulder buttons on top
    for s in (-1, 1):
        sh = box("sh", (0.36, 0.2, 0.06), (s * 0.43, 0.02, H / 2 + 0.01), clay2, 0.025)
        parts.append(sh)
    o = join("handheld", parts + [scr])
    return shade(o, 35)


# ------------------------------------------------------------ kanban

def kanban():
    graphite, clay, clay2, glow, steel, ink = M("graphite"), M("clay"), M("clay2"), M("glow"), M("steel"), M("ink")
    parts = [plate("kb_board", 3.2, 2.2, 0.14, 0.1, graphite, 0.03, -0.07)]
    # frame rail on top with a little tray at the bottom
    parts.append(box("kb_tray", (2.6, 0.22, 0.05), (0, -0.12, -1.07), steel, 0.015))
    cols = [(-1.03, 3), (0, 2), (1.03, 2)]
    for ci, (x, n) in enumerate(cols):
        lane = plate("kb_lane", 0.92, 1.88, 0.02, 0.05, clay2, 0.006, -0.09)
        lane.location = (x, 0, -0.04)
        apply_transform(lane)
        parts.append(lane)
        hd = box("kb_head", (0.5, 0.01, 0.06), (x - 0.15, -0.1, 0.78), ink)
        parts.append(hd)
        for k in range(n):
            z = 0.5 - k * 0.47
            m = glow if (ci == 1 and k == 0) else clay
            card = plate("kb_card", 0.78, 0.38, 0.04, 0.035, m, 0.01, -0.14)
            card.rotation_euler = (0, math.radians((k * 7 + ci * 5) % 5 - 2), 0)
            card.location = (x, 0, z)
            apply_transform(card)
            parts.append(card)
            for li, w in enumerate((0.5, 0.36)):
                parts.append(box("kb_line", (w, 0.01, 0.035), (x - 0.3 + w / 2, -0.145, z + 0.07 - li * 0.08), ink if m is not glow else graphite))
            parts.append(sphere("kb_dot", 0.03, (x + 0.29, -0.145, z - 0.11), 12, 6, steel if m is not glow else graphite))
            # magnet pin
            parts.append(cylinder("kb_pin", 0.035, 0.03, (x, -0.17, z + 0.16), 16, steel))
            parts[-1].rotation_euler = (math.pi / 2, 0, 0)
            parts[-1].data.transform(Matrix.Translation((-x, 0.17, -(z + 0.16))))
            apply_transform(parts[-1])
            parts[-1].location = (x, -0.17, z + 0.16)
            apply_transform(parts[-1])
    o = join("kanban", parts)
    return shade(o, 35)


# ------------------------------------------------------------ jar

def jar():
    glass, steel, clay, glow, paper, ink = M("glass"), M("steel"), M("clay"), M("glow"), M("paper"), M("ink")
    outer = [(0.0, 0.0), (0.58, 0.0), (0.68, 0.04), (0.73, 0.14), (0.75, 0.3), (0.75, 1.25), (0.72, 1.4), (0.6, 1.52), (0.5, 1.58), (0.5, 1.72)]
    glass_j = lathe("jar_glass", catmull(outer, 4), 64, glass, cap=True)
    solidify(glass_j, 0.03, -1)
    parts = [glass_j]
    # threaded neck rings
    for k in range(3):
        z = 1.6 + k * 0.035
        parts.append(lathe("jar_thread", [(0.5, z), (0.515, z + 0.008), (0.515, z + 0.016), (0.5, z + 0.024)], 64, glass))
    # lid with knurled edge
    lid = []
    segs = 96
    for zi, r in ((1.66, 0.55), (1.92, 0.55)):
        pass
    rings = []
    for z in (1.66, 1.68, 1.9, 1.92):
        ring = []
        for s in range(segs):
            th = TAU * s / segs
            rr = 0.555 + (0.012 if s % 2 == 0 and 1.67 < z < 1.91 else 0)
            if z in (1.66, 1.92):
                rr = 0.54
            ring.append((rr * math.cos(th), rr * math.sin(th), z))
        rings.append(ring)
    lid_o = loft("jar_lid", rings, steel)
    parts.append(lid_o)
    parts.append(lathe("jar_lidtop", [(0.54, 1.92), (0.5, 1.94), (0.2, 1.95), (0.0, 1.95)], 64, steel))
    # label band
    lab = lathe("jar_label", [(0.765, 0.62), (0.765, 0.9)], 64, paper, cap=False)
    solidify(lab, 0.006, 1)
    parts.append(lab)
    parts.append(lathe("jar_labline", [(0.774, 0.74), (0.774, 0.78)], 64, ink, cap=False))
    parts[-1].data.polygons.foreach_set("use_smooth", [True] * len(parts[-1].data.polygons))
    solidify(parts[-1], 0.004, 1)
    # contents: a heap of beans/marbles
    import random
    rnd = random.Random(4)
    for k in range(34):
        r = rnd.uniform(0.1, 0.15)
        a = rnd.uniform(0, TAU)
        d = rnd.uniform(0, 0.55 - r)
        layer = k // 11
        z = 0.06 + r + layer * 0.21 + rnd.uniform(0, 0.05)
        parts.append(sphere("jar_bean", r, (d * math.cos(a), d * math.sin(a), z), 16, 8, glow if k % 5 == 0 else clay, zscale=0.8))
    o = join("jar", parts, origin=(0, 0, 0.95))
    return shade(o, 40)


# ------------------------------------------------------------ terminal

def terminal():
    graphite, clay2, glow, steel, ink, clay = M("graphite"), M("clay2"), M("glow"), M("steel"), M("ink"), M("clay")
    W, H = 3.3, 2.15
    parts = [plate("tm_win", W, H, 0.16, 0.12, graphite, 0.03, -0.08)]
    bar = plate("tm_bar", W - 0.06, 0.26, 0.02, 0.09, M("rubber"), 0.006, -0.1)
    bar.location = (0, 0, H / 2 - 0.16)
    apply_transform(bar)
    parts.append(bar)
    for i, m in enumerate((M("paperShade"), clay2, glow)):
        d = cylinder("tm_dot", 0.045, 0.03, (0, 0, 0), 20, m)
        d.rotation_euler = (math.pi / 2, 0, 0)
        d.location = (-W / 2 + 0.2 + i * 0.14, -0.11, H / 2 - 0.16)
        apply_transform(d)
        parts.append(d)
    parts.append(box("tm_tab", (0.7, 0.01, 0.05), (0, -0.115, H / 2 - 0.16), clay2))
    # code lines: prompt glyph + tokens of varying length
    lines = [(0, [(0.12, glow), (0.9, clay), (0.5, clay2)]),
             (1, [(0.3, clay2), (1.1, clay2)]),
             (1, [(0.3, clay2), (0.6, glow), (0.4, clay2)]),
             (0, [(0.12, glow), (0.7, clay), (0.35, clay)]),
             (1, [(0.3, clay2), (1.35, clay2)]),
             (1, [(0.3, clay2), (0.5, clay2), (0.8, glow)]),
             (0, [(0.12, glow)])]
    z = H / 2 - 0.5
    for indent, toks in lines:
        x = -W / 2 + 0.25 + indent * 0.18
        for w, m in toks:
            parts.append(box("tm_tok", (w, 0.015, 0.075), (x + w / 2, -0.095, z), m, 0.006))
            x += w + 0.08
        z -= 0.21
    # blinking cursor block (the site blinks it)
    cur = box("cursor", (0.08, 0.02, 0.13), (-W / 2 + 0.25 + 0.2 + 0.04, -0.1, z + 0.21), glow)
    o = join("terminal", parts)
    shade(o, 35)
    cur.location = (0, 0, 0)
    return [o, cur]


def build(coll):
    objs = []
    h = handheld(); objs.append(h)
    k = kanban(); objs.append(k)
    j = jar(); objs.append(j)
    t, cur = terminal(); objs += [t, cur]
    cur.parent = t
    for i, o in enumerate([h, k, j, t]):
        o.location = (-6 + i * 4, 0, 0)
    for o in objs:
        for c in o.users_collection:
            c.objects.unlink(o)
        coll.objects.link(o)
    return objs
