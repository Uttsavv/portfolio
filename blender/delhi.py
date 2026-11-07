"""Hero scene: Qutub Minar, India Gate, Jama Masjid, the Lotus Temple, Humayun's Tomb and an auto-rickshaw, in steel-blue clay."""
import math
import random
from lib import *  # noqa: F401,F403
from lib import MATS


def M(name):
    return MATS[name]


# ------------------------------------------------------------ Qutub Minar

def qutub():
    parts = []
    clay, clay2, dark = M("clay"), M("clay2"), M("clayDark")
    H = 5.9
    r_bottom, r_top = 0.6, 0.2

    def R(z):
        return r_bottom + (r_top - r_bottom) * (z / H)

    # storey: (z0, z1, flute pattern, flutes, amp)
    storeys = [
        (0.16, 2.35, "alt", 24, 0.085),
        (2.52, 3.62, "round", 20, 0.075),
        (3.78, 4.55, "angle", 16, 0.08),
        (4.70, 5.18, "plain", 0, 0.0),
        (5.33, 5.62, "plain", 0, 0.0),
    ]

    def flute(u, kind, k):
        if kind == "round" or (kind == "alt" and k % 2 == 0):
            return math.sin(math.pi * u) ** 0.8
        return 1 - abs(2 * u - 1)

    for si, (z0, z1, kind, n, amp) in enumerate(storeys):
        rings = []
        rows = max(2, int((z1 - z0) / 0.1))
        per = 8
        segs = n * per if n else 48
        for rI in range(rows + 1):
            z = z0 + (z1 - z0) * rI / rows
            base = R(z) * (1 - amp * 0.6 if n else 1)
            ring = []
            for s in range(segs):
                th = TAU * s / segs
                if n:
                    k, u = divmod(s, per)
                    u = u / per
                    rr = base * (1 + amp * flute(u, kind, k))
                else:
                    rr = base
                ring.append((rr * math.cos(th), rr * math.sin(th), z))
            rings.append(ring)
        shaft = loft(f"q_shaft{si}", rings, clay if si < 3 else M("marble"))
        parts.append(shaft)

        # inscription bands around the fluted storeys
        if n:
            for f in (0.22, 0.5) if si == 0 else (0.35,):
                zb = z0 + (z1 - z0) * f
                rb = R(zb) * (1 + amp * 0.55)
                parts.append(lathe(f"q_band{si}{f}", [(rb, zb - 0.025), (rb + 0.012, zb - 0.02), (rb + 0.012, zb + 0.02), (rb, zb + 0.025)], 64, clay2))

        # balcony at the top of each storey: stepped corbel rings, brackets, deck and a pierced parapet
        if si < 4:
            zt = z1
            rt = R(zt) * (1 + amp * 0.5)
            prof = [(rt - 0.01, zt - 0.12), (rt + 0.03, zt - 0.1), (rt + 0.03, zt - 0.07), (rt + 0.07, zt - 0.05), (rt + 0.07, zt - 0.03), (rt + 0.12, zt - 0.01), (rt + 0.12, zt + 0.02), (rt - 0.02, zt + 0.02)]
            parts.append(lathe(f"q_corbel{si}", prof, 72, clay2))
            nb = 28 - si * 4
            for b in range(nb):
                th = TAU * (b + 0.5) / nb
                cx, cy = (rt + 0.05) * math.cos(th), (rt + 0.05) * math.sin(th)
                br = box(f"q_br{si}_{b}", (0.08, 0.035, 0.07), (0, 0, 0), clay2)
                br.rotation_euler = (0, 0, th)
                br.location = (cx, cy, zt - 0.1)
                apply_transform(br)
                parts.append(br)
            # parapet: thin ring wall with small posts
            ro = rt + 0.115
            parts.append(lathe(f"q_par{si}", [(ro - 0.012, zt + 0.02), (ro, zt + 0.02), (ro, zt + 0.1), (ro - 0.012, zt + 0.1)], 72, clay))
            parts.append(lathe(f"q_rail{si}", [(ro - 0.016, zt + 0.1), (ro + 0.006, zt + 0.1), (ro + 0.006, zt + 0.118), (ro - 0.016, zt + 0.118)], 72, clay2))

    # plinth
    parts.append(lathe("q_plinth", [(0.82, 0), (0.82, 0.08), (0.74, 0.08), (0.74, 0.16), (0.6, 0.16)], 8 * 4, clay2))
    # cupola on top: drum, little dome, finial
    zt = 5.62
    parts.append(cylinder("q_drum", 0.17, 0.08, (0, 0, zt), 32, clay2))
    for b in range(8):
        th = TAU * b / 8
        parts.append(cylinder(f"q_col{b}", 0.013, 0.18, (0.13 * math.cos(th), 0.13 * math.sin(th), zt + 0.08), 8, M("marble")))
    parts.append(cylinder("q_cap", 0.18, 0.03, (0, 0, zt + 0.26), 32, clay2))
    parts.append(lathe("q_dome", [(0.15, zt + 0.29), (0.15, zt + 0.32), (0.13, zt + 0.38), (0.08, zt + 0.43), (0.03, zt + 0.455), (0.0, zt + 0.46)], 32, M("marble")))
    parts.append(lathe("q_fin", [(0.012, zt + 0.45), (0.025, zt + 0.48), (0.012, zt + 0.51), (0.004, zt + 0.56), (0.0, zt + 0.57)], 12, clay2))
    o = join("qutub", parts)
    return shade(o, 50)


# ------------------------------------------------------------ India Gate

def india_gate():
    clay, clay2, marble = M("clay"), M("clay2"), M("marble")
    W, D, Hb = 3.2, 1.0, 3.0
    parts = []
    body = box("ig_body", (W, D, Hb - 0.2), (0, 0, 0.2 + (Hb - 0.2) / 2), clay)
    # archivolts (raised arch rings) front and back, impost bands and pilasters are joined before cutting
    adds = []
    ring_out = arch_points(1.42, 1.7, 0, 24)
    adds.append(prism("ig_archivolt", ring_out, -D / 2 - 0.035, D / 2 + 0.035, clay2))
    for side in (-1, 1):
        x = side * (W / 2 - 0.16)
        adds.append(box(f"ig_pil{side}", (0.2, D + 0.05, Hb - 0.45), (x, 0, 0.2 + (Hb - 0.45) / 2), clay2))
        adds.append(box(f"ig_impost{side}", (0.95, D + 0.04, 0.07), (side * 1.05, 0, 1.7), clay2))
    for a in adds:
        boolean(body, a, "UNION")
    # main arch through the depth, side arches through the width
    cut_main = prism("ig_cut", arch_points(1.1, 1.7, 0, 32, base=-0.1), -1, 1)
    boolean(body, cut_main)
    cut_side = prism("ig_cut2", arch_points(0.5, 0.95, 0, 20, base=-0.1), -2.0, 2.0)
    cut_side.rotation_euler = (0, 0, math.pi / 2)
    cut_side.location = (0, 0, 0.2)
    apply_transform(cut_side)
    boolean(body, cut_side)
    # recessed panels on the piers (front and back)
    for side in (-1, 1):
        for fy in (-1, 1):
            p = box("ig_rec", (0.42, 0.06, 0.95), (side * 1.07, fy * D / 2, 2.35), None)
            boolean(body, p)
    bevel_mod(body, 0.035, 3)
    parts.append(body)

    # plinth steps
    parts.append(box("ig_step0", (W + 0.7, D + 0.5, 0.1), (0, 0, 0.05), clay2, 0.03))
    parts.append(box("ig_step1", (W + 0.4, D + 0.3, 0.1), (0, 0, 0.15), clay2, 0.03))
    # cornice stack
    z = Hb
    for w, d, h, m in [(W + 0.18, D + 0.16, 0.06, clay2), (W + 0.3, D + 0.26, 0.1, clay), (W + 0.22, D + 0.2, 0.05, clay2)]:
        parts.append(box("ig_corn", (w, d, h), (0, 0, z + h / 2), m, 0.02))
        z += h
    # attic with the inscription panel
    attic = box("ig_attic", (W - 0.1, D - 0.04, 0.42), (0, 0, z + 0.21), clay)
    for fy in (-1, 1):
        boolean(attic, box("ig_panel", (2.3, 0.04, 0.24), (0, fy * (D - 0.04) / 2, z + 0.21), None))
    bevel_mod(attic, 0.03, 3)
    parts.append(attic)
    for fy in (-1, 1):
        t = text_mesh("ig_text", "INDIA", 0.2, 0.012, marble)
        t.rotation_euler = (math.pi / 2, 0, 0 if fy < 0 else math.pi)
        t.location = (0, fy * ((D - 0.04) / 2 - 0.02), z + 0.21)
        apply_transform(t)
        parts.append(t)
    z += 0.42
    for w, d, h, m in [(W + 0.02, D + 0.06, 0.05, clay2), (2.55, 0.85, 0.2, clay), (2.62, 0.9, 0.04, clay2), (2.05, 0.72, 0.16, clay)]:
        parts.append(box("ig_top", (w, d, h), (0, 0, z + h / 2), m, 0.02))
        z += h
    # shallow dome and the bowl on top
    parts.append(cylinder("ig_drum", 0.46, 0.08, (0, 0, z), 48, clay2))
    z += 0.08
    parts.append(lathe("ig_dome", [(0.44, z), (0.43, z + 0.05), (0.38, z + 0.11), (0.28, z + 0.16), (0.15, z + 0.19), (0.0, z + 0.2)], 48, clay))
    z += 0.18
    parts.append(cylinder("ig_stem", 0.04, 0.06, (0, 0, z - 0.02), 16, clay2))
    parts.append(lathe("ig_bowl", [(0.03, z), (0.06, z + 0.03), (0.06, z + 0.06), (0.16, z + 0.09), (0.24, z + 0.15), (0.26, z + 0.18), (0.22, z + 0.18), (0.14, z + 0.13), (0.0, z + 0.12)], 40, marble, cap=False))
    o = join("indiaGate", parts)
    return shade(o, 50)


# ------------------------------------------------------------ Jama Masjid

def chhatri(prefix, r, h, loc, mats):
    clay, clay2, marble = mats
    x, y, z = loc
    p = [cylinder(prefix + "base", r * 1.1, h * 0.08, (x, y, z), 24, clay2)]
    for b in range(8):
        th = TAU * b / 8
        p.append(cylinder(prefix + f"c{b}", r * 0.08, h * 0.42, (x + r * 0.85 * math.cos(th), y + r * 0.85 * math.sin(th), z + h * 0.08), 8, clay))
    z2 = z + h * 0.5
    eave = lathe(prefix + "eave", [(r * 1.25, z2), (r * 1.25, z2 + h * 0.04), (r * 0.95, z2 + h * 0.08)], 24, clay2)
    eave.location = (x, y, 0)
    apply_transform(eave)
    p.append(eave)
    dome = lathe(prefix + "dome", [(a + 0, b) for a, b in onion_profile(r * 0.95, h * 0.45)], 24, marble)
    dome.location = (x, y, z2 + h * 0.08)
    apply_transform(dome)
    p.append(dome)
    p.append(cylinder(prefix + "fin", r * 0.05, h * 0.18, (x, y, z2 + h * 0.5), 6, clay2, r2=0.0))
    return p


def minaret(prefix, H, loc, mats, stripe):
    clay, clay2, marble = mats
    x, y, z = loc
    p = []
    rb, rt = 0.2, 0.13
    levels = [0, 0.42, 0.72, 0.9]
    for li in range(3):
        z0, z1 = z + H * levels[li], z + H * levels[li + 1]
        r0 = rb + (rt - rb) * levels[li]
        r1 = rb + (rt - rb) * levels[li + 1]
        sh = loft(prefix + f"s{li}", [circle(r0, z0 + 0.02, 16, x, y, TAU / 32), circle(r1, z1, 16, x, y, TAU / 32)], clay)
        # vertical marble stripes on alternate facets
        paint_faces(sh, stripe, lambda c, n, x=x, y=y: abs(n.z) < 0.5 and int(((math.atan2(c.y - y, c.x - x) + math.pi) / TAU * 16) + 0.5) % 2 == 0)
        p.append(sh)
        # balcony
        p.append(lathe(prefix + f"b{li}", [(r1 - 0.01, z1 - 0.1), (r1 + 0.07, z1 - 0.02), (r1 + 0.09, z1), (r1 + 0.09, z1 + 0.025), (r1 - 0.01, z1 + 0.025)], 32, clay2))
        p[-1].location = (x, y, 0)
        apply_transform(p[-1])
        p.append(lathe(prefix + f"p{li}", [(r1 + 0.075, z1 + 0.025), (r1 + 0.09, z1 + 0.025), (r1 + 0.09, z1 + 0.08), (r1 + 0.075, z1 + 0.08)], 32, clay))
        p[-1].location = (x, y, 0)
        apply_transform(p[-1])
    p += chhatri(prefix + "ch", 0.16, 0.62, (x, y, z + H * 0.9 + 0.03), mats)
    return p


def jama_masjid():
    clay, clay2, marble, stripe = M("clay"), M("clay2"), M("marble"), M("clayDark")
    mats = (clay, clay2, marble)
    parts = []
    # high plinth with a flight of steps at the front
    parts.append(box("jm_plinth", (7.2, 2.2, 0.42), (0, 0, 0.21), clay2, 0.04))
    for i in range(5):
        parts.append(box(f"jm_st{i}", (1.6 - i * 0.12, 0.16, 0.084 * (i + 1)), (0, 1.1 + 0.16 * (4 - i) + 0.08, 0.042 * (i + 1)), clay2, 0.004))
    z0 = 0.42
    # prayer hall with arched bays
    hall = box("jm_hall", (5.6, 1.3, 1.05), (0, 0, z0 + 0.525), clay)
    for side in (-1, 1):
        for k in range(5):
            x = side * (1.0 + 0.36 * k)
            c = prism("jm_bay", arch_points(0.24, 0.45, 0.25, 12, base=0.1), 0.55, 0.8)
            c.location = (x, 0, z0)
            apply_transform(c)
            boolean(hall, c)
    bevel_mod(hall, 0.03, 3)
    parts.append(hall)
    # merlons along the parapet
    for k in range(-26, 27):
        parts.append(box("jm_mer", (0.06, 0.06, 0.08), (k * 0.105, 0.62, z0 + 1.09), clay2))
    parts.append(box("jm_cor", (5.7, 1.36, 0.05), (0, 0, z0 + 1.05), clay2))
    # the pishtaq: tall frontal gate with a deep pointed arch, framed by little minarets
    pish = box("jm_pish", (1.5, 1.5, 1.75), (0, 0.1, z0 + 0.875), clay)
    c = prism("jm_iwan", arch_points(0.9, 0.95, 0.3, 24, base=0.0), 0.35, 1.2)
    c.location = (0, 0, z0)
    apply_transform(c)
    boolean(pish, c)
    frame = box("jm_frame", (1.1, 0.06, 1.42), (0, 0.86, z0 + 0.71), None)
    boolean(pish, frame)
    bevel_mod(pish, 0.03, 3)
    parts.append(pish)
    for side in (-1, 1):
        parts.append(cylinder(f"jm_turret{side}", 0.06, 1.9, (side * 0.77, 0.85, z0), 12, clay2))
        parts += chhatri(f"jm_tch{side}", 0.09, 0.35, (side * 0.77, 0.85, z0 + 1.9), mats)
    for k in range(-6, 7):
        parts.append(box("jm_pm", (0.07, 0.06, 0.09), (k * 0.115, 0.83, z0 + 1.79), clay2))
    # three striped onion domes on drums
    for x, r, h in ((-1.55, 0.5, 1.0), (0, 0.7, 1.35), (1.55, 0.5, 1.0)):
        zb = z0 + 1.05
        parts.append(cylinder("jm_drum", r * 0.74, 0.28 * h, (x, -0.1, zb), 48, clay))
        parts.append(lathe("jm_drumcap", [(r * 0.8, zb + 0.28 * h), (r * 0.8, zb + 0.3 * h), (r * 0.7, zb + 0.32 * h)], 48, clay2))
        parts[-1].location = (x, -0.1, 0)
        apply_transform(parts[-1])
        d = lathe("jm_dome", onion_profile(r, h), 48, marble)
        d.location = (x, -0.1, zb + 0.3 * h)
        apply_transform(d)
        # vertical stripes like the real domes
        paint_faces(d, stripe, lambda c, n, x=x: int(((math.atan2(c.y + 0.1, c.x - x) + math.pi) / TAU * 48)) % 4 == 0)
        parts.append(d)
        zt = zb + 0.3 * h + h
        parts.append(lathe("jm_kalash", [(0.035, zt - 0.02), (0.06, zt + 0.03), (0.035, zt + 0.08), (0.05, zt + 0.12), (0.02, zt + 0.17), (0.008, zt + 0.32), (0.0, zt + 0.34)], 12, clay2))
        parts[-1].location = (x, -0.1, 0)
        apply_transform(parts[-1])
    # two tall minarets at the ends
    for side in (-1, 1):
        parts += minaret(f"jm_min{side}", 3.6, (side * 3.25, 0.2, z0), mats, stripe)
    o = join("jamaMasjid", parts)
    return shade(o, 50)


# ------------------------------------------------------------ skyline

def tower(name, w, d, h, seed):
    rnd = random.Random(seed)
    clay2, dark = M("clay2"), M("clayDark")
    parts = [box(name + "c", (w, d, h), (0, 0, h / 2), clay2, 0.015)]
    # floor plates
    z = 0.28
    while z < h - 0.1:
        parts.append(box(name + "f", (w + 0.04, d + 0.04, 0.025), (0, 0, z), dark))
        z += 0.22
    # crown: setback block and a mast on some
    if rnd.random() < 0.6:
        parts.append(box(name + "s", (w * 0.6, d * 0.6, 0.3), (0, 0, h + 0.15), clay2, 0.01))
        if rnd.random() < 0.6:
            parts.append(cylinder(name + "m", 0.015, 0.5, (0, 0, h + 0.3), 6, dark))
    return join(name, parts)


def skyline():
    out = []
    # Blender +Y is "behind" once exported (glTF -Z)
    spec = [(-8.6, 6.4, 1.0, 2.4), (-7.4, 5.6, 0.8, 3.6), (-6.3, 6.8, 0.9, 2.0), (-5.3, 5.9, 0.7, 2.8),
            (4.8, 6.1, 0.9, 2.7), (5.8, 5.4, 0.8, 4.0), (6.8, 6.5, 1.0, 2.2), (7.8, 5.7, 0.75, 3.1), (8.8, 6.7, 0.9, 1.8)]
    for i, (x, y, w, h) in enumerate(spec):
        t = tower(f"tower{i}", w, w * 0.9, h, i)
        t.location = (x, y, 0)
        out.append(shade(t, 30))
    return out



# ------------------------------------------------------------ Lotus Temple

def petal(name, L, W, cup, tilt, rot, r0, mat, rows=14, cols=10):
    """One marble petal: a pointed, cupped shell standing on a ring of radius r0, tilted out by `tilt`, turned by `rot`."""
    bm = bmesh.new()
    grid = []
    ct, st = math.cos(tilt), math.sin(tilt)
    cr, sr = math.cos(rot), math.sin(rot)
    for i in range(rows + 1):
        u = i / rows
        w = W * (math.sin(math.pi * min(1.0, u * 0.92 + 0.08)) ** 0.75) * (1 - 0.55 * u)
        row = []
        for j in range(cols + 1):
            v = -1 + 2 * j / cols
            x = v * w
            y = -cup * (1 - v * v) * w - 0.12 * L * u * u  # cupped across, curling in near the tip
            z = L * u
            # tilt outward (about local x), then push out to the ring and turn round the centre
            y2, z2 = y * ct - z * st, y * st + z * ct
            y2 -= r0
            row.append(bm.verts.new((x * cr - y2 * sr, x * sr + y2 * cr, z2)))
        grid.append(row)
    for i in range(rows):
        for j in range(cols):
            bm.faces.new((grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]))
    o = mesh_obj(name, bm, mat)
    solidify(o, 0.035, 0)
    for f in o.data.polygons:
        f.use_smooth = True
    return o


def lotus_temple():
    marble, clay2, dark = M("marble"), M("clay"), M("clay2")
    parts = []
    # podium: three nine-sided steps, with the pools as darker rings
    for k, (r, z0, z1, m) in enumerate([(1.55, 0, 0.12, dark), (1.32, 0.12, 0.2, clay2), (1.12, 0.2, 0.3, marble)]):
        ring = lathe(f"lt_step{k}", [(0.0, z0), (r, z0), (r, z1), (0.0, z1)], 9, m)
        ring.rotation_euler = (0, 0, math.pi / 9)
        parts.append(ring)
    # three rings of nine petals: inner closed bud, middle half open, outer arching out like canopies
    for k in range(9):
        a = 2 * math.pi * k / 9
        parts.append(petal(f"lt_in{k}", 1.35, 0.34, 0.55, math.radians(-8), a, 0.22, marble))
        parts.append(petal(f"lt_mid{k}", 1.1, 0.42, 0.5, math.radians(22), a + math.pi / 9, 0.5, marble))
        parts.append(petal(f"lt_out{k}", 0.85, 0.46, 0.45, math.radians(62), a, 0.86, marble))
    for o in parts[3:]:
        o.location.z += 0.3
    return join("lotus", parts)


# ------------------------------------------------------------ auto-rickshaw

def auto_rickshaw():
    clay, blue, rubber, steel, glow, dark = M("clay"), M("blue"), M("rubber"), M("steel"), M("glow"), M("clayDark")
    parts = []
    # floor pan and rear seat box
    parts.append(box("ar_floor", (0.62, 1.05, 0.1), (0, 0.02, 0.2), clay, 0.03))
    parts.append(box("ar_seat", (0.6, 0.34, 0.24), (0, 0.34, 0.36), dark, 0.04))
    # front cowl: a tapered nose with the windscreen frame above
    nose = loft("ar_nose", [
        [(-0.31, -0.28, 0.15), (0.31, -0.28, 0.15), (0.31, -0.28, 0.62), (-0.31, -0.28, 0.62)],
        [(-0.2, -0.52, 0.15), (0.2, -0.52, 0.15), (0.16, -0.48, 0.56), (-0.16, -0.48, 0.56)],
    ], clay)
    bevel_mod(nose, 0.03, 2, 30)
    parts.append(nose)
    parts.append(box("ar_screen", (0.5, 0.03, 0.34), (0, -0.3, 0.8), M("glass"), 0.01))
    # canopy: a rounded hood over the cabin
    rings = []
    for i in range(9):
        y = -0.34 + 0.86 * i / 8
        drop = 0.04 * (1 - (2 * i / 8 - 1) ** 2)
        ring = []
        for j in range(13):
            t = math.pi * j / 12
            ring.append((0.34 * math.cos(t), y, 0.98 + drop + 0.16 * math.sin(t)))
        rings.append(ring)
    hood = loft("ar_hood", rings, blue, cap_bottom=True, cap_top=True, closed=False)
    solidify(hood, 0.025, 0)
    parts.append(hood)
    for x in (-0.31, 0.31):
        parts.append(cylinder("ar_post", 0.016, 0.66, (x, 0.48, 0.3), 10, steel))
        parts.append(cylinder("ar_postf", 0.016, 0.36, (x, -0.3, 0.62), 10, steel))
    # wheels: one at the front, two at the back
    for (x, y) in ((0, -0.42), (-0.33, 0.36), (0.33, 0.36)):
        w = cylinder("ar_wheel", 0.13, 0.08, (0, 0, -0.04), 24, rubber, bevel=0.02)
        w.rotation_euler = (0, math.pi / 2, 0)
        w.location = (x, y, 0.13)
        parts.append(w)
    parts.append(sphere("ar_lamp", 0.045, (0, -0.53, 0.5), 16, 8, glow))
    return join("auto", parts)



# ------------------------------------------------------------ Humayun's Tomb

def humayun_tomb():
    clay, clay2, dark, marble = M("clay"), M("clay2"), M("clayDark"), M("marble")
    parts = []
    # arcaded plinth: a broad low platform with a row of arched niches on each face
    PW, PH = 3.0, 0.5
    parts.append(box("ht_plinth", (PW, PW, PH), (0, 0, PH / 2), clay2, 0.02))
    n = 7
    for side in range(4):
        for k in range(n):
            x = -PW / 2 + PW * (k + 0.5) / n
            niche = prism("ht_niche", arch_points(0.24, 0.2, 0.25, 8), -0.02, 0.02, dark)
            niche.location = (x, -PW / 2 - 0.005, 0.08)
            niche.rotation_euler = (0, 0, 0)
            apply_transform(niche)
            niche.data.transform(Matrix.Rotation(side * math.pi / 2, 4, "Z"))
            parts.append(niche)
    # main block with chamfered corners
    B, BH = 1.9, 1.25
    blk = box("ht_block", (B, B, BH), (0, 0, PH + BH / 2), clay, 0.0)
    bevel_mod(blk, 0.32, 1, 60)
    parts.append(blk)
    # tall central arch (pishtaq) on every face, framed in marble
    for side in range(4):
        fr = box("ht_frame", (0.86, 0.06, 1.12), (0, -B / 2 - 0.01, PH + 0.6), marble, 0.01)
        ar = prism("ht_arch", arch_points(0.6, 0.62, 0.3, 12), -0.05, 0.02, dark)
        ar.location = (0, -B / 2 - 0.035, PH + 0.08)
        apply_transform(ar)
        for o in (fr, ar):
            o.data.transform(Matrix.Rotation(side * math.pi / 2, 4, "Z"))
            parts.append(o)
    # drum and the great double dome in marble
    top = PH + BH
    parts.append(cylinder("ht_drum", 0.62, 0.32, (0, 0, top), 40, clay2))
    dome = lathe("ht_dome", [(0.6, 0), (0.7, 0.18), (0.74, 0.42), (0.66, 0.72), (0.46, 0.95), (0.22, 1.08), (0.0, 1.12)], 48, marble)
    dome.location = (0, 0, top + 0.32)
    apply_transform(dome)
    parts.append(dome)
    parts.append(cylinder("ht_fin", 0.035, 0.32, (0, 0, top + 1.42), 8, clay2, r2=0.0))
    # chhatris on the four corners of the roof
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts += chhatri(f"ht_c{sx}{sy}", 0.17, 0.62, (sx * 0.62, sy * 0.62, top), (clay, clay2, marble))
    return join("humayun", parts)


def build(coll):
    objs = []
    # overlapping like a pop-up book: Qutub front-left, India Gate front-right, Jama Masjid behind both
    # a spread-out skyline so nothing hides: Qutub left, Jama Masjid behind the gap, India Gate centre-right,
    # the Lotus Temple and Humayun's Tomb filling the right, an auto-rickshaw parked in front
    q = qutub(); q.location = (-3.3, -0.2, 0); objs.append(q)
    j = jama_masjid(); j.location = (-1.0, 3.6, 0); j.rotation_euler = (0, 0, math.pi); j.scale = (1.12, 1.12, 1.12); objs.append(j)
    g = india_gate(); g.location = (1.3, -0.3, 0); g.scale = (0.92, 0.92, 0.92); objs.append(g)
    lt = lotus_temple(); lt.location = (4.0, 0.6, 0); lt.scale = (1.25, 1.25, 1.25); objs.append(lt)
    ht = humayun_tomb(); ht.location = (4.6, 4.2, 0); ht.scale = (1.2, 1.2, 1.2); objs.append(ht)
    ar = auto_rickshaw(); ar.location = (-1.0, -1.9, 0); ar.rotation_euler = (0, 0, math.radians(-28)); ar.scale = (1.35, 1.35, 1.35); objs.append(ar)
    for o in objs:
        for c in o.users_collection:
            c.objects.unlink(o)
        coll.objects.link(o)
    return objs
