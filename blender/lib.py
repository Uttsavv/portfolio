"""Small modelling helpers for the portfolio scenes (bpy, Blender 4.2+ / 5.x).

Everything is built procedurally so the models can be regenerated with:
    python blender/build.py        (needs `pip install bpy`)
Blender is Z-up; the glTF exporter converts to Y-up.
"""
import math
import bmesh
import bpy
from mathutils import Matrix, Vector

TAU = math.tau


# ---------------------------------------------------------------- scene

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def link(obj, coll=None):
    (coll or bpy.context.scene.collection).objects.link(obj)
    return obj


def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


# ---------------------------------------------------------------- materials

MATS = {}


def material(name, color, rough=0.5, metal=0.0, emit=None, emit_strength=0.0, transmission=0.0, ior=1.45, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*srgb_to_linear(color), 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if emit:
        p.inputs["Emission Color"].default_value = (*srgb_to_linear(emit), 1)
        p.inputs["Emission Strength"].default_value = emit_strength
    if transmission:
        p.inputs["Transmission Weight"].default_value = transmission
        p.inputs["IOR"].default_value = ior
    if alpha < 1:
        p.inputs["Alpha"].default_value = alpha
    MATS[name] = m
    return m


def srgb_to_linear(hexstr):
    h = hexstr.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return out


# ---------------------------------------------------------------- mesh building

def mesh_obj(name, bm, mat=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    link(obj)
    if mat is not None:
        obj.data.materials.append(mat)
    return obj


def loft(name, rings, mat=None, cap_bottom=True, cap_top=True, closed=True):
    """rings: list of lists of (x, y, z); every ring has the same vertex count."""
    bm = bmesh.new()
    vs = [[bm.verts.new(p) for p in ring] for ring in rings]
    n = len(rings[0])
    for a, b in zip(vs, vs[1:]):
        for i in range(n if closed else n - 1):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
    if cap_bottom:
        bm.faces.new(list(reversed(vs[0])))
    if cap_top:
        bm.faces.new(vs[-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj(name, bm, mat)


def circle(r, z, segs, cx=0.0, cy=0.0, phase=0.0):
    return [(cx + r * math.cos(phase + TAU * i / segs), cy + r * math.sin(phase + TAU * i / segs), z) for i in range(segs)]


def lathe(name, profile, segs=48, mat=None, cap=True):
    """profile: list of (radius, z) from bottom to top."""
    rings = []
    for r, z in profile:
        rings.append(circle(max(r, 1e-4), z, segs))
    return loft(name, rings, mat, cap_bottom=cap and profile[0][0] > 1e-3, cap_top=cap and profile[-1][0] > 1e-3)


def prism(name, pts2d, y0, y1, mat=None):
    """Extrude a closed polygon drawn in the XZ plane along Y from y0 to y1."""
    bm = bmesh.new()
    a = [bm.verts.new((x, y0, z)) for x, z in pts2d]
    b = [bm.verts.new((x, y1, z)) for x, z in pts2d]
    n = len(pts2d)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj(name, bm, mat)


def prism_xy(name, pts2d, z0, z1, mat=None):
    """Extrude a closed polygon drawn in the XY plane along Z."""
    bm = bmesh.new()
    a = [bm.verts.new((x, y, z0)) for x, y in pts2d]
    b = [bm.verts.new((x, y, z1)) for x, y in pts2d]
    n = len(pts2d)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    bm.faces.new(list(reversed(a)))
    bm.faces.new(b)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj(name, bm, mat)


def box(name, size, loc=(0, 0, 0), mat=None, bevel=0.0, segs=2):
    sx, sy, sz = size
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=bm.verts)
    bmesh.ops.translate(bm, vec=loc, verts=bm.verts)
    o = mesh_obj(name, bm, mat)
    if bevel:
        bevel_mod(o, bevel, segs)
    return o


def cylinder(name, r, h, loc=(0, 0, 0), segs=32, mat=None, r2=None, bevel=0.0):
    r2 = r if r2 is None else r2
    x, y, z = loc
    o = loft(name, [circle(r, z, segs, x, y), circle(r2, z + h, segs, x, y)], mat)
    if bevel:
        bevel_mod(o, bevel, 2)
    return o


def sphere(name, r, loc=(0, 0, 0), segs=32, rings=16, mat=None, zscale=1.0, cut=1.0):
    """UV sphere; `cut` < 1 keeps only the top part (1 = full, .5 = hemisphere)."""
    prof = []
    for k in range(rings + 1):
        t = k / rings
        th = math.pi * (1 - cut) + (math.pi * cut) * t  # from bottom-ish to top
        th = math.pi - th
        prof.append((r * math.sin(th), r * math.cos(th) * zscale))
    prof.sort(key=lambda p: p[1])
    o = lathe(name, prof, segs, mat)
    o.location = loc
    apply_transform(o)
    return o


def text_mesh(name, body, size, extrude, mat=None, align="CENTER"):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.align_x = align
    cu.align_y = "CENTER"
    tmp = bpy.data.objects.new(name + "_tmp", cu)
    link(tmp)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    o = bpy.data.objects.new(name, me)
    link(o)
    if mat is not None:
        o.data.materials.clear()
        o.data.materials.append(mat)
    return o


# ---------------------------------------------------------------- modifiers (applied without bpy.ops)

def _bake(obj):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(obj.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
    old = obj.data
    obj.modifiers.clear()
    obj.data = me
    if old.users == 0:
        bpy.data.meshes.remove(old)
    return obj


def bevel_mod(obj, width, segs=2, angle=40):
    m = obj.modifiers.new("bevel", "BEVEL")
    m.width = width
    m.segments = segs
    m.limit_method = "ANGLE"
    m.angle_limit = math.radians(angle)
    m.harden_normals = False
    m.miter_outer = "MITER_ARC"
    return _bake(obj)


def boolean(obj, cutter, op="DIFFERENCE", remove=True):
    m = obj.modifiers.new("bool", "BOOLEAN")
    m.operation = op
    m.object = cutter
    m.solver = "EXACT"
    m.use_self = True
    m.use_hole_tolerant = True
    _bake(obj)
    if remove:
        bpy.data.objects.remove(cutter)
    return obj


def solidify(obj, t, offset=-1):
    m = obj.modifiers.new("solid", "SOLIDIFY")
    m.thickness = t
    m.offset = offset
    return _bake(obj)


def subdivide(obj, levels=1):
    m = obj.modifiers.new("subd", "SUBSURF")
    m.levels = levels
    m.render_levels = levels
    return _bake(obj)


def apply_transform(obj):
    obj.data.transform(obj.matrix_basis)
    obj.matrix_basis = Matrix.Identity(4)
    return obj


def join(name, objs, origin=(0, 0, 0)):
    """Merge objects into one mesh (materials kept) whose origin is `origin` (world)."""
    mats = []
    bm = bmesh.new()
    for o in objs:
        apply_transform(o)
        me = o.data
        remap = []
        for m in me.materials:
            if m not in mats:
                mats.append(m)
            remap.append(mats.index(m))
        n0 = len(bm.faces)
        bm.from_mesh(me)
        bm.faces.ensure_lookup_table()
        for f in bm.faces[n0:]:
            f.material_index = remap[f.material_index] if remap else 0
    bmesh.ops.translate(bm, vec=Vector(origin) * -1, verts=bm.verts)
    for o in objs:
        me = o.data
        bpy.data.objects.remove(o)
        if me.users == 0:
            bpy.data.meshes.remove(me)
    out = mesh_obj(name, bm)
    for m in mats:
        out.data.materials.append(m)
    out.location = origin
    return out


def shade(obj, angle=35):
    """Smooth shading with sharp edges above `angle` (auto-smooth equivalent)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    lim = math.radians(angle)
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:
        if len(e.link_faces) == 2:
            e.smooth = e.calc_face_angle(0) < lim
        else:
            e.smooth = False
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def set_material(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.material_index = 0
    return obj


def paint_faces(obj, mat, pred):
    """Assign `mat` to faces whose centre satisfies pred(center, normal)."""
    if mat not in list(obj.data.materials):
        obj.data.materials.append(mat)
    idx = list(obj.data.materials).index(mat)
    for p in obj.data.polygons:
        if pred(p.center, p.normal):
            p.material_index = idx
    return obj


# ---------------------------------------------------------------- shapes

def arch_points(w, spring, pointed=0.0, segs=16, base=0.0):
    """Arch outline in XZ: span w, springing height `spring`.
    pointed=0 is a round arch; >0 makes a two-centred pointed arch (radius = w/2 * (1 + pointed))."""
    r = w / 2 * (1 + pointed)
    cl = -w / 2 + r  # centre of the left arc (x)
    th_a = math.acos(max(-1, min(1, (0 - cl) / r)))  # angle where the left arc reaches x=0
    left = []
    for k in range(segs + 1):
        th = math.pi - (math.pi - th_a) * k / segs
        left.append((cl + r * math.cos(th), spring + r * math.sin(th)))
    right = [(-x, z) for x, z in reversed(left[:-1])]
    return [(-w / 2, base)] + left + right + [(w / 2, base)]


def catmull(pts, per=6):
    """Smooth a 2D polyline with a Catmull-Rom spline (endpoints kept)."""
    out = []
    P = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(per):
            t = k / per
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[d]) + (-p0[d] + p2[d]) * t + (2 * p0[d] - 5 * p1[d] + 4 * p2[d] - p3[d]) * t2 + (-p0[d] + 3 * p1[d] - 3 * p2[d] + p3[d]) * t3) for d in range(2)))
    out.append(tuple(pts[-1]))
    return out


ONION = [(0.66, 0.0), (0.8, 0.07), (0.96, 0.2), (1.0, 0.33), (0.94, 0.48), (0.76, 0.63), (0.5, 0.76), (0.26, 0.87), (0.1, 0.95), (0.0, 1.0)]


def onion_profile(r, h):
    return [(max(0.0, x * r), z * h) for x, z in catmull(ONION, 5)]
