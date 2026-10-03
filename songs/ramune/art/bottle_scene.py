"""Blender (Cycles) scene for the ラムネ cover: a Codd-neck ramune bottle modelled by
revolving a profile (2.2 mm glass walls), the glass marble in its chamber, soda with a
level surface and rising bubbles, condensation droplets, lit by a Nishita sky and a sun,
in front of a camera-facing backdrop that carries the painted sky and cloud (bg.png from
make_art.py --bg), so the glass refracts the same sky the sleeve shows.

    blender -b --factory-startup -P bottle_scene.py -- --size 1000 --samples 64 --out render.png
"""
import math
import random
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
opt = {"--size": "1000", "--samples": "64", "--out": str(HERE / "render.png")}
for i in range(0, len(args) - 1, 2):
    opt[args[i]] = args[i + 1]
SIZE, SAMPLES, OUT = int(opt["--size"]), int(opt["--samples"]), opt["--out"]
rng = random.Random(813)

TILT = math.radians(-9)          # bottle leans left in the picture
T = 0.0022                       # glass wall
SEG = 160                        # segments around

# outer radius profile (z, r) in metres: base, body, shoulder, lower pinch, marble chamber,
# upper pinch, neck, lip
PROFILE = [(0.000, 0.0262), (0.003, 0.0302), (0.008, 0.0310), (0.096, 0.0310), (0.106, 0.0298),
           (0.116, 0.0252), (0.124, 0.0184), (0.1305, 0.0142), (0.137, 0.0166), (0.149, 0.0196),
           (0.161, 0.0176), (0.1685, 0.0128), (0.177, 0.0119), (0.195, 0.0123), (0.1995, 0.0141),
           (0.2045, 0.0141), (0.2060, 0.0129)]
MARBLE_Z, MARBLE_R = 0.1495, 0.0128
LEVEL = 0.098                    # soda level (world height, bottle base at z=0 before the tilt)


def catmull(points, n):
    """Smooth (Catmull-Rom) resampling of the (z, r) profile."""
    pts = [points[0]] + points + [points[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        steps = max(2, int(n * (p2[0] - p1[0]) / (points[-1][0] - points[0][0])) + 2)
        for k in range(steps):
            t = k / steps
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(points[-1])
    return out


def lathe(rings, name, cap_bottom=True, cap_top=False):
    """Mesh from rings [(z, r)], revolved around Z; caps as triangle fans."""
    bm = bmesh.new()
    loops = []
    for z, r in rings:
        loops.append([bm.verts.new((r * math.cos(2 * math.pi * k / SEG), r * math.sin(2 * math.pi * k / SEG), z))
                      for k in range(SEG)])
    for a, b in zip(loops, loops[1:]):
        for k in range(SEG):
            bm.faces.new((a[k], a[(k + 1) % SEG], b[(k + 1) % SEG], b[k]))
    if cap_bottom:
        c = bm.verts.new((0, 0, rings[0][0]))
        for k in range(SEG):
            bm.faces.new((loops[0][(k + 1) % SEG], loops[0][k], c))
    if cap_top:
        c = bm.verts.new((0, 0, rings[-1][0]))
        for k in range(SEG):
            bm.faces.new((loops[-1][k], loops[-1][(k + 1) % SEG], c))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def bottle():
    outer = catmull(PROFILE, 260)
    inner = [(z, max(0.0015, r - T)) for z, r in outer if 0.0045 <= z <= outer[-1][0] - 0.0004]
    # one closed solid: outer surface up, across the lip, inner surface down to the inner floor
    rings = outer + list(reversed(inner))
    bm = bmesh.new()
    loops = []
    for z, r in rings:
        loops.append([bm.verts.new((r * math.cos(2 * math.pi * k / SEG), r * math.sin(2 * math.pi * k / SEG), z))
                      for k in range(SEG)])
    for a, b in zip(loops, loops[1:]):
        for k in range(SEG):
            bm.faces.new((a[k], a[(k + 1) % SEG], b[(k + 1) % SEG], b[k]))
    for ring, flip in ((loops[0], True), (loops[-1], False)):
        c = bm.verts.new((0, 0, ring[0].co.z))
        for k in range(SEG):
            f = (ring[(k + 1) % SEG], ring[k], c) if flip else (ring[k], ring[(k + 1) % SEG], c)
            bm.faces.new(f)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("bottle")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new("bottle", me)
    bpy.context.collection.objects.link(ob)
    return ob, inner


def soda(inner, world):
    """Soda: the inner profile shrunk by 0.15 mm, cut by the level world plane."""
    rings = [(z, r - 0.00015) for z, r in inner if z <= 0.118]
    ob = lathe([(rings[0][0] + 0.0002, rings[0][1])] + rings, "soda", cap_bottom=True, cap_top=True)
    ob.data.transform(world)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, LEVEL),
                                 plane_no=(0, 0, 1), clear_outer=True)
    edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
    bmesh.ops.holes_fill(bm, edges=edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def inner_r(inner, z):
    for (z0, r0), (z1, r1) in zip(inner, inner[1:]):
        if z0 <= z <= z1:
            return r0 + (r1 - r0) * (z - z0) / max(1e-9, z1 - z0)
    return inner[-1][1]


def outer_r(z):
    prof = catmull(PROFILE, 260)
    for (z0, r0), (z1, r1) in zip(prof, prof[1:]):
        if z0 <= z <= z1:
            return r0 + (r1 - r0) * (z - z0) / max(1e-9, z1 - z0)
    return prof[-1][1]


def sphere(name, r, mat, segments=32, rings=16):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=rings, radius=r)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(mat)
    return me


def material(name, color, ior, rough=0.0, absorb=None, glass_node=False):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    if glass_node:
        sh = nt.nodes.new("ShaderNodeBsdfGlass")
        sh.inputs["Color"].default_value = (*color, 1)
        sh.inputs["IOR"].default_value = ior
        sh.inputs["Roughness"].default_value = rough
    else:
        sh = nt.nodes.new("ShaderNodeBsdfPrincipled")
        sh.inputs["Base Color"].default_value = (*color, 1)
        sh.inputs["Roughness"].default_value = rough
        sh.inputs["IOR"].default_value = ior
        sh.inputs["Transmission Weight"].default_value = 1.0
    nt.links.new(sh.outputs[0], out.inputs["Surface"])
    if absorb:
        va = nt.nodes.new("ShaderNodeVolumeAbsorption")
        va.inputs["Color"].default_value = (*absorb[0], 1)
        va.inputs["Density"].default_value = absorb[1]
        nt.links.new(va.outputs[0], out.inputs["Volume"])
    return m


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    world_m = Matrix.Rotation(TILT, 4, "Y")

    glass = material("glass", (0.82, 0.97, 0.98), 1.50, 0.0, ((0.55, 0.88, 0.90), 35))
    sodam = material("soda", (0.94, 0.99, 1.0), 1.33, 0.0, ((0.80, 0.96, 0.98), 3))
    marblem = material("marble", (0.80, 0.95, 1.0), 1.52, 0.0, ((0.40, 0.78, 0.95), 45))
    bubm = material("bubble", (1, 1, 1), 0.752, 0.0, glass_node=True)
    dropm = material("drop", (1, 1, 1), 1.33, 0.0, glass_node=True)

    bot, inner = bottle()
    bot.data.materials.append(glass)
    bot.matrix_world = world_m
    so = soda(inner, world_m)
    so.data.materials.append(sodam)

    mar = bpy.data.objects.new("marble", sphere("marble", MARBLE_R, marblem, 96, 48))
    bpy.context.collection.objects.link(mar)
    mar.matrix_world = world_m @ Matrix.Translation((0.0012, 0, MARBLE_Z))

    # bubbles: columns rising from the floor and walls, a few clinging to the wall
    bub = sphere("bubble", 1.0, bubm, 16, 8)
    for col in range(10):
        ang = rng.uniform(0, 2 * math.pi)
        z = rng.uniform(0.006, 0.03)
        rr = rng.uniform(0.0, 0.8)
        while z < 0.112:
            r_in = inner_r(inner, z) - 0.0012
            p = Vector((math.cos(ang) * r_in * rr, math.sin(ang) * r_in * rr, z))
            w = world_m @ p
            if w.z > LEVEL - 0.0012:
                break
            s = rng.uniform(0.0002, 0.0006) * (1 + z * 4)
            ob = bpy.data.objects.new("b", bub)
            ob.matrix_world = Matrix.Translation(w) @ Matrix.Scale(s, 4)
            bpy.context.collection.objects.link(ob)
            z += rng.uniform(0.004, 0.011)
            ang += rng.uniform(-0.15, 0.15)
    for _ in range(55):
        z = rng.uniform(0.008, 0.09)
        ang = rng.uniform(0, 2 * math.pi)
        r_in = inner_r(inner, z) - 0.0006
        w = world_m @ Vector((math.cos(ang) * r_in, math.sin(ang) * r_in, z))
        if w.z > LEVEL - 0.001:
            continue
        ob = bpy.data.objects.new("bw", bub)
        ob.matrix_world = Matrix.Translation(w) @ Matrix.Scale(rng.uniform(0.0003, 0.0006), 4)
        bpy.context.collection.objects.link(ob)
    # condensation on the cold body, below the soda line
    drop = sphere("drop", 1.0, dropm, 20, 10)
    for _ in range(70):
        z = rng.uniform(0.01, 0.1)
        ang = rng.uniform(-math.pi * 0.95, -math.pi * 0.05)      # the half facing the camera
        r_o = outer_r(z)
        n = Vector((math.cos(ang), math.sin(ang), 0))
        size = rng.uniform(0.0005, 0.0014)
        p = Vector((math.cos(ang) * r_o, math.sin(ang) * r_o, z)) + n * size * 0.15
        rot = n.to_track_quat("Z", "Y").to_matrix().to_4x4()
        ob = bpy.data.objects.new("d", drop)
        ob.matrix_world = world_m @ Matrix.Translation(p) @ rot @ Matrix.Diagonal((size, size * 1.25, size * 0.45, 1))
        bpy.context.collection.objects.link(ob)

    # camera: low angle, 85 mm, the neck and marble above centre, the body cut by the frame
    cam_d = bpy.data.cameras.new("cam")
    cam_d.lens = 85
    cam_d.sensor_width = 36
    cam = bpy.data.objects.new("cam", cam_d)
    bpy.context.collection.objects.link(cam)
    cam.location = (0.045, -0.47, 0.105)
    target = Vector((0.028, 0, 0.136))
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam

    # backdrop: the painted sky, camera-facing; its middle third fills the frame exactly and
    # the rest extends the edge pixels, so wide-angle views (the marble is a lens) never see
    # the plane's border
    dist = 7.0
    half = dist * (18 / 85) * 1.01
    k = 3.0
    me = bpy.data.meshes.new("backdrop")
    me.from_pydata([(-k * half, -k * half, 0), (k * half, -k * half, 0), (k * half, k * half, 0),
                    (-k * half, k * half, 0)], [], [(0, 1, 2, 3)])
    me.uv_layers.new()
    lo, hi = 0.5 - k / 2, 0.5 + k / 2
    for li, uv in zip(me.loops, [(lo, lo), (hi, lo), (hi, hi), (lo, hi)]):
        me.uv_layers.active.data[li.index].uv = uv
    bd = bpy.data.objects.new("backdrop", me)
    bpy.context.collection.objects.link(bd)
    bd.parent = cam
    bd.location = (0, 0, -dist)
    bm_ = bpy.data.materials.new("backdrop")
    bm_.use_nodes = True
    nt = bm_.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(HERE / "bg.png"))
    tex.extension = "EXTEND"
    em = nt.nodes.new("ShaderNodeEmission")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    me.materials.append(bm_)
    bd.visible_shadow = False

    # light: Nishita sky + sun from the upper left, a little in front
    w = bpy.data.worlds.new("sky")
    sc.world = w
    w.use_nodes = True
    sky = w.node_tree.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "NISHITA"
    sky.sun_elevation = math.radians(52)
    sky.sun_rotation = math.radians(215)
    sky.altitude = 0
    sky.air_density, sky.dust_density = 1.0, 1.2
    bgn = w.node_tree.nodes["Background"]
    bgn.inputs["Strength"].default_value = 0.35
    # below the horizon the Nishita sky is black: a pale summer haze there instead, so the
    # marble (a lens that shows the world upside down) never shows a dark hole
    tc = w.node_tree.nodes.new("ShaderNodeTexCoord")
    sep = w.node_tree.nodes.new("ShaderNodeSeparateXYZ")
    rmp = w.node_tree.nodes.new("ShaderNodeMapRange")
    rmp.inputs["From Min"].default_value, rmp.inputs["From Max"].default_value = -0.02, 0.12
    mix = w.node_tree.nodes.new("ShaderNodeMixRGB")
    mix.inputs["Color1"].default_value = (2.2, 2.6, 3.0, 1)
    w.node_tree.links.new(tc.outputs["Generated"], sep.inputs[0])
    w.node_tree.links.new(sep.outputs["Z"], rmp.inputs["Value"])
    w.node_tree.links.new(rmp.outputs["Result"], mix.inputs["Fac"])
    w.node_tree.links.new(sky.outputs["Color"], mix.inputs["Color2"])
    w.node_tree.links.new(mix.outputs[0], bgn.inputs["Color"])
    sun_d = bpy.data.lights.new("sun", "SUN")
    sun_d.energy = 4.5
    sun_d.angle = math.radians(1.5)
    sun = bpy.data.objects.new("sun", sun_d)
    bpy.context.collection.objects.link(sun)
    sun.rotation_euler = Vector((0.55, 0.65, -0.52)).to_track_quat("-Z", "Y").to_euler()
    # a soft fill from the right so the shadow side of the glass keeps an edge
    fill_d = bpy.data.lights.new("fill", "AREA")
    fill_d.energy = 6
    fill_d.shape = "DISK"
    fill_d.size = 0.6
    fill = bpy.data.objects.new("fill", fill_d)
    bpy.context.collection.objects.link(fill)
    fill.location = (0.6, -0.3, 0.3)
    fill.rotation_euler = (Vector((0, 0, 0.12)) - fill.location).to_track_quat("-Z", "Y").to_euler()

    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = False     # Ubuntu's Blender has no OIDN: adaptive sampling + oversampling
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.006
    sc.cycles.max_bounces = 24
    sc.cycles.transmission_bounces = 24
    sc.cycles.transparent_max_bounces = 24
    sc.cycles.glossy_bounces = 12
    sc.cycles.caustics_reflective = True
    sc.cycles.caustics_refractive = True
    sc.cycles.blur_glossy = 0.6
    sc.cycles.sample_clamp_indirect = 8
    sc.render.resolution_x = sc.render.resolution_y = SIZE
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = OUT
    bpy.ops.render.render(write_still=True)
    print("rendered", OUT)


main()
