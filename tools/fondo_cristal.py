"""AxolOS · fondo de pantalla de cristal líquido (Blender + Cycles).

El ajolote de AxolOS como escultura de cristal: su silueta se «infla» resolviendo una ecuación de
Poisson (∇²u = −1 dentro de la forma, u = 0 en el borde; altura ∝ √u), así cuerpo, branquias y
dedos tienen sección redonda. El cristal tiene dispersión real (tres capas de vidrio con índices
distintos para rojo, verde y azul) e irisación de película fina.

  oscuro  (por defecto): agua negra con reflejos de aceite irisados y luces de color (imágenes 2 y 4)
  claro:  superficie clara, cielo pálido azulado y luz de día (imagen 1)

Uso:
  blender -b --factory-startup --python tools/fondo_cristal.py -- \\
      --modo oscuro --salida fondo.png [--ancho 3840 --alto 2160 --muestras 512]
"""
import argparse
import math
import sys
from pathlib import Path

import bpy
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
SILUETA = RAIZ / "packages/axolos-branding/files/ajolote-silueta.svg"
MORADO = (0.651, 0.604, 0.996)     # #a69afe, el morado de AxolOS


def argumentos():
    a = argparse.ArgumentParser()
    a.add_argument("--modo", choices=("oscuro", "claro"), default="oscuro")
    a.add_argument("--salida", required=True)
    a.add_argument("--ancho", type=int, default=3840)
    a.add_argument("--alto", type=int, default=2160)
    a.add_argument("--muestras", type=int, default=512)
    a.add_argument("--resolucion-forma", type=int, default=1100, help="píxeles de la silueta para la malla")
    a.add_argument("--solo-ajolote", action="store_true",
                   help="solo el ajolote sobre fondo transparente, encuadrado (arranque, logos)")
    return a.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])


# ---- forma: silueta → máscara → inflado ----------------------------------------------------------
# El Python de Blender no trae Qt: la silueta la rasteriza el Python del sistema
RASTER = """
import sys, numpy as np
from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor, QGuiApplication, QImage, QPainter
from PyQt6.QtSvg import QSvgRenderer
n = int(sys.argv[2]); app = QGuiApplication(["fondo"])
img = QImage(n, n, QImage.Format.Format_Grayscale8); img.fill(QColor("white"))
p = QPainter(img); p.setRenderHint(QPainter.RenderHint.Antialiasing)
QSvgRenderer(sys.argv[1]).render(p, QRectF(0, 0, n, n)); p.end()
b = img.constBits(); b.setsize(img.sizeInBytes())
np.save(sys.argv[3], np.frombuffer(b, np.uint8).reshape(n, img.bytesPerLine())[:, :n] < 128)
"""


def mascara(n):
    """Silueta del ajolote (dentro = True), n×n."""
    import os
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        destino = os.path.join(d, "m.npy")
        entorno = dict(os.environ, QT_QPA_PLATFORM="offscreen")
        entorno.pop("PYTHONHOME", None)
        entorno.pop("PYTHONPATH", None)
        subprocess.run(["/usr/bin/python3", "-I", "-c", RASTER, str(SILUETA), str(n), destino], check=True, env=entorno)
        return np.load(destino)


def _reducir(m):
    h, w = m.shape[0] // 2 * 2, m.shape[1] // 2 * 2
    return m[:h, :w].reshape(h // 2, 2, w // 2, 2).all(axis=(1, 3))


def inflar(m):
    """Altura redonda: resuelve ∇²u = −1 en la máscara (u = 0 fuera), de grueso a fino; devuelve √u.
    En una franja de ancho w, √u es una semicircunferencia: branquias, dedos y cuerpo salen redondos."""
    niveles = [m]
    while niveles[-1].shape[0] > 70:
        niveles.append(_reducir(niveles[-1]))
    u = None
    for i, nivel in enumerate(reversed(niveles)):
        paso2 = (m.shape[0] / nivel.shape[0]) ** 2
        if u is None:
            u = np.zeros(nivel.shape)
        else:
            u = np.kron(u, np.ones((2, 2)))
            u = np.pad(u, ((0, max(0, nivel.shape[0] - u.shape[0])), (0, max(0, nivel.shape[1] - u.shape[1]))))
            u = u[:nivel.shape[0], :nivel.shape[1]]
        for _ in range(900 if i == 0 else 160):
            vec = (np.roll(u, 1, 0) + np.roll(u, -1, 0) + np.roll(u, 1, 1) + np.roll(u, -1, 1)) * 0.25
            u = np.where(nivel, vec + paso2 * 0.25, 0.0)
    return np.sqrt(np.maximum(u, 0.0))


def malla(m, h, escala=4.0, grosor=0.30, fondo=0.38, nombre="malla", suavizar=10):
    """Malla cerrada a partir de una máscara m y su altura h (0…1): cara superior a +h·grosor,
    inferior a −fondo·h·grosor, unidas en el borde (h = 0). Centrada; el lado de la máscara mide «escala»."""
    n = m.shape[0]
    dentro = m
    borde = ~m & (np.roll(m, 1, 0) | np.roll(m, -1, 0) | np.roll(m, 1, 1) | np.roll(m, -1, 1)
                  | np.roll(np.roll(m, 1, 0), 1, 1) | np.roll(np.roll(m, -1, 0), -1, 1)
                  | np.roll(np.roll(m, 1, 0), -1, 1) | np.roll(np.roll(m, -1, 0), 1, 1))
    usar = dentro | borde
    ys, xs = np.nonzero(usar)
    k = escala / n
    X, Y = (xs - n / 2) * k, (n / 2 - ys) * k
    alt = np.where(dentro[ys, xs], h[ys, xs] * grosor, 0.0)
    sup = -np.ones(usar.shape, np.int64)
    sup[ys, xs] = np.arange(len(ys))
    ni, nj = np.nonzero(dentro)
    inf = sup.copy()
    inf[ni, nj] = len(ys) + np.arange(len(ni))
    verts = np.concatenate([np.stack([X, Y, alt], 1),
                            np.stack([(nj - n / 2) * k, (n / 2 - ni) * k, -h[ni, nj] * grosor * fondo], 1)])
    a, b = usar[:-1, :-1] & usar[1:, :-1], usar[:-1, 1:] & usar[1:, 1:]
    i, j = np.nonzero(a & b)
    q_sup = np.stack([sup[i, j], sup[i + 1, j], sup[i + 1, j + 1], sup[i, j + 1]], 1)
    q_inf = np.stack([inf[i, j + 1], inf[i + 1, j + 1], inf[i + 1, j], inf[i, j]], 1)
    caras = np.concatenate([q_sup, q_inf])
    me = bpy.data.meshes.new(nombre)
    me.vertices.add(len(verts))
    me.vertices.foreach_set("co", verts.astype(np.float32).ravel())
    me.loops.add(caras.size)
    me.loops.foreach_set("vertex_index", caras.astype(np.int32).ravel())
    me.polygons.add(len(caras))
    me.polygons.foreach_set("loop_start", (np.arange(len(caras)) * 4).astype(np.int32))
    me.polygons.foreach_set("loop_total", np.full(len(caras), 4, np.int32))
    me.update(calc_edges=True)
    me.validate()
    me.shade_smooth()
    ob = bpy.data.objects.new(nombre, me)
    bpy.context.collection.objects.link(ob)
    if suavizar:   # la malla sigue la cuadrícula de píxeles: suavizado laplaciano, contorno sin dientes
        sua = ob.modifiers.new("suave", "SMOOTH")
        sua.factor, sua.iterations = 0.75, suavizar
    return ob


def malla_ajolote(n, escala=4.0, grosor=0.30, fondo=0.38):
    m = mascara(n)
    h = inflar(m)
    return malla(m, h / h.max(), escala, grosor, fondo, "ajolote")


# ---- materiales ----------------------------------------------------------------------------------
def nodo(nt, tipo, x, y, **valores):
    n = nt.nodes.new(tipo)
    n.location = (x, y)
    for k, v in valores.items():
        n.inputs[k].default_value = v
    return n


def cristal(nombre, ior=1.47, dispersion=0.035, rugosidad=0.0, pelicula=(250.0, 620.0), tinte=(1, 1, 1)):
    """Vidrio con dispersión (R, G y B con índices distintos) e irisación de película fina variable."""
    mat = bpy.data.materials.new(nombre)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    sal = nodo(nt, "ShaderNodeOutputMaterial", 900, 0)
    tex = nodo(nt, "ShaderNodeTexNoise", -700, 300, Scale=1.6, Detail=6.0, Roughness=0.55)
    rampa = nodo(nt, "ShaderNodeMapRange", -450, 300)
    rampa.inputs["To Min"].default_value, rampa.inputs["To Max"].default_value = pelicula
    nt.links.new(tex.outputs["Fac"], rampa.inputs["Value"])
    suma = None
    for k, (canal, d) in enumerate((((1, 0, 0), -dispersion), ((0, 1, 0), 0.0), ((0, 0, 1), dispersion))):
        c = tuple(a * b for a, b in zip(canal, tinte)) + (1,)
        g = nodo(nt, "ShaderNodeBsdfGlass", 0, 250 - k * 250, Color=c, IOR=ior + d, Roughness=rugosidad)
        nt.links.new(rampa.outputs["Result"], g.inputs["Thin Film Thickness"])
        g.inputs["Thin Film IOR"].default_value = 1.38
        if suma is None:
            suma = g
        else:
            s = nodo(nt, "ShaderNodeAddShader", 300 + k * 150, 100)
            nt.links.new(suma.outputs[0], s.inputs[0])
            nt.links.new(g.outputs[0], s.inputs[1])
            suma = s
    nt.links.new(suma.outputs[0], sal.inputs["Surface"])
    return mat


def emisor(nombre, color, fuerza):
    mat = bpy.data.materials.new(nombre)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    e = nodo(nt, "ShaderNodeEmission", 0, 0, Color=tuple(color) + (1,), Strength=fuerza)
    sal = nodo(nt, "ShaderNodeOutputMaterial", 250, 0)
    nt.links.new(e.outputs[0], sal.inputs["Surface"])
    return mat


def emisor_suave(nombre, color, fuerza):
    """Luz de panel que se apaga hacia los bordes: sus reflejos son manchas suaves, no rectángulos."""
    mat = bpy.data.materials.new(nombre)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    coord = nodo(nt, "ShaderNodeTexCoord", -900, 0)
    mapa = nt.nodes.new("ShaderNodeMapping")
    mapa.location = (-700, 0)
    mapa.inputs["Location"].default_value = (-1.0, -1.0, 0.0)
    mapa.inputs["Scale"].default_value = (2.0, 2.0, 1.0)
    nt.links.new(coord.outputs["Generated"], mapa.inputs["Vector"])
    grad = nt.nodes.new("ShaderNodeTexGradient")
    grad.gradient_type = "SPHERICAL"
    grad.location = (-500, 0)
    nt.links.new(mapa.outputs["Vector"], grad.inputs["Vector"])
    pot = nodo(nt, "ShaderNodeMath", -300, 0)
    pot.operation = "POWER"
    pot.inputs[1].default_value = 2.2
    nt.links.new(grad.outputs["Fac"], pot.inputs[0])
    mult = nodo(nt, "ShaderNodeMath", -120, 0)
    mult.operation = "MULTIPLY"
    mult.inputs[1].default_value = fuerza
    nt.links.new(pot.outputs[0], mult.inputs[0])
    e = nodo(nt, "ShaderNodeEmission", 80, 0, Color=tuple(color) + (1,))
    nt.links.new(mult.outputs[0], e.inputs["Strength"])
    sal = nodo(nt, "ShaderNodeOutputMaterial", 300, 0)
    nt.links.new(e.outputs[0], sal.inputs["Surface"])
    return mat


def aceite(nombre, fuerza):
    """Bandas de color de una mancha de aceite (naranja → magenta → morado → azul → turquesa) en X,
    apagándose hacia arriba y abajo. Solo se ve reflejado en el agua."""
    mat = bpy.data.materials.new(nombre)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    coord = nodo(nt, "ShaderNodeTexCoord", -1100, 0)
    sep = nodo(nt, "ShaderNodeSeparateXYZ", -900, 0)
    nt.links.new(coord.outputs["Generated"], sep.inputs[0])
    ruido = nodo(nt, "ShaderNodeTexNoise", -900, -250, Scale=2.5, Detail=3.0)
    nt.links.new(coord.outputs["Generated"], ruido.inputs["Vector"])
    mezcla = nodo(nt, "ShaderNodeMath", -700, 0)
    mezcla.operation = "MULTIPLY_ADD"
    mezcla.inputs[1].default_value = 0.18
    nt.links.new(ruido.outputs["Fac"], mezcla.inputs[0])
    nt.links.new(sep.outputs["X"], mezcla.inputs[2])
    rampa = nt.nodes.new("ShaderNodeValToRGB")
    rampa.location = (-500, 0)
    els = rampa.color_ramp.elements
    els[0].position, els[0].color = 0.05, (1.0, 0.40, 0.08, 1)
    els[1].position, els[1].color = 1.05, (0.10, 0.85, 0.75, 1)
    for pos, col in ((0.30, (1.0, 0.22, 0.55, 1)), (0.52, MORADO + (1,)), (0.76, (0.08, 0.35, 1.0, 1))):
        els.new(pos).color = col
    nt.links.new(mezcla.outputs[0], rampa.inputs["Fac"])
    # se apaga arriba y abajo
    vert = nt.nodes.new("ShaderNodeMapRange")
    vert.location = (-700, -450)
    nt.links.new(sep.outputs["Y"], vert.inputs["Value"])
    seno = nodo(nt, "ShaderNodeMath", -500, -450)
    seno.operation = "SINE"
    escala = nodo(nt, "ShaderNodeMath", -620, -450)
    escala.operation = "MULTIPLY"
    escala.inputs[1].default_value = math.pi
    nt.links.new(sep.outputs["Y"], escala.inputs[0])
    nt.links.new(escala.outputs[0], seno.inputs[0])
    ondas = nt.nodes.new("ShaderNodeTexWave")
    ondas.location = (-700, -650)
    ondas.wave_type, ondas.bands_direction = "BANDS", "Y"
    ondas.inputs["Scale"].default_value = 2.2
    ondas.inputs["Distortion"].default_value = 2.0
    ondas.inputs["Detail"].default_value = 3.0
    nt.links.new(coord.outputs["Generated"], ondas.inputs["Vector"])
    banda = nodo(nt, "ShaderNodeMath", -500, -650)
    banda.operation = "POWER"
    banda.inputs[1].default_value = 1.2
    nt.links.new(ondas.outputs["Fac"], banda.inputs[0])
    junto = nodo(nt, "ShaderNodeMath", -400, -450)
    junto.operation = "MULTIPLY"
    nt.links.new(seno.outputs[0], junto.inputs[0])
    nt.links.new(banda.outputs[0], junto.inputs[1])
    mult = nodo(nt, "ShaderNodeMath", -300, -300)
    mult.operation = "MULTIPLY"
    mult.inputs[1].default_value = fuerza
    nt.links.new(junto.outputs[0], mult.inputs[0])
    e = nt.nodes.new("ShaderNodeEmission")
    e.location = (-100, 0)
    nt.links.new(rampa.outputs["Color"], e.inputs["Color"])
    nt.links.new(mult.outputs[0], e.inputs["Strength"])
    sal = nodo(nt, "ShaderNodeOutputMaterial", 150, 0)
    nt.links.new(e.outputs[0], sal.inputs["Surface"])
    return mat


def superficie(nombre, base, rugosidad, pelicula):
    """Agua / superficie pulida con película fina (reflejos irisados de aceite)."""
    mat = bpy.data.materials.new(nombre)
    mat.use_nodes = True
    nt = mat.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = tuple(base) + (1,)
    p.inputs["Roughness"].default_value = rugosidad
    p.inputs["IOR"].default_value = 1.33
    if pelicula:
        tex = nodo(nt, "ShaderNodeTexNoise", -700, 300, Scale=0.35, Detail=4.0, Roughness=0.6, Distortion=1.5)
        r = nodo(nt, "ShaderNodeMapRange", -450, 300)
        r.inputs["To Min"].default_value, r.inputs["To Max"].default_value = pelicula
        nt.links.new(tex.outputs["Fac"], r.inputs["Value"])
        nt.links.new(r.outputs["Result"], p.inputs["Thin Film Thickness"])
        p.inputs["Thin Film IOR"].default_value = 1.45
    geo = nodo(nt, "ShaderNodeNewGeometry", -950, -300)
    rizo = nodo(nt, "ShaderNodeTexNoise", -700, -300, Scale=0.22, Detail=2.0, Roughness=0.45)
    nt.links.new(geo.outputs["Position"], rizo.inputs["Vector"])
    bump = nodo(nt, "ShaderNodeBump", -400, -300, Strength=0.11, Distance=1.0)
    nt.links.new(rizo.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    return mat


# ---- escena --------------------------------------------------------------------------------------
def plano(nombre, tam, pos, rot=(0, 0, 0), mat=None, sub=0, ondas=0.0):
    bpy.ops.mesh.primitive_plane_add(size=1, location=pos, rotation=rot)
    ob = bpy.context.object
    ob.name = nombre
    ob.scale = (tam[0], tam[1], 1)
    if sub:
        m = ob.modifiers.new("sub", "SUBSURF")
        m.subdivision_type = "SIMPLE"
        m.levels = m.render_levels = sub
    if ondas:
        t = bpy.data.textures.new(nombre + "-ondas", "CLOUDS")
        t.noise_scale = 2.6
        t.noise_depth = 2
        d = ob.modifiers.new("ondas", "DISPLACE")
        d.texture = t
        d.texture_coords = "GLOBAL"      # olas en metros, no estiradas por la escala del plano
        d.strength = ondas
        d.mid_level = 0.5
        ob.modifiers.new("suave", "SMOOTH").iterations = 4
        bpy.ops.object.shade_smooth()
    if mat:
        ob.data.materials.append(mat)
    return ob


def luz_area(nombre, pos, mira, color, energia, tam):
    d = bpy.data.lights.new(nombre, "AREA")
    d.color, d.energy, d.size = color, energia, tam
    d.shape = "DISK"
    ob = bpy.data.objects.new(nombre, d)
    bpy.context.collection.objects.link(ob)
    ob.location = pos
    ob.rotation_euler = _mirar(np.array(mira, float) - np.array(pos, float))
    ob.visible_camera = False          # se ve su reflejo y su refracción, no el disco de luz
    return ob


def _mirar(v):
    from mathutils import Vector
    return Vector(v).to_track_quat("-Z", "Y").to_euler()


def esfera_luz(pos, radio, color, fuerza):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radio, location=pos, segments=24, ring_count=12)
    ob = bpy.context.object
    ob.data.materials.append(emisor("luz", color, fuerza))
    ob.visible_shadow = False
    return ob


def cinta(nombre, puntos, ancho, grosor, mat):
    """Cinta de cristal (como la imagen 2): curva con sección elíptica."""
    perfil = bpy.data.curves.new(nombre + "-perfil", "CURVE")
    perfil.dimensions = "2D"
    s = perfil.splines.new("NURBS")
    pts = [(math.cos(t) * ancho, math.sin(t) * grosor, 0, 1) for t in np.linspace(0, 2 * math.pi, 17)[:-1]]
    s.points.add(len(pts) - 1)
    for p, c in zip(s.points, pts):
        p.co = c
    s.use_cyclic_u = True
    s.order_u = 4
    ob_p = bpy.data.objects.new(nombre + "-perfil", perfil)
    bpy.context.collection.objects.link(ob_p)
    ob_p.hide_render = True
    cu = bpy.data.curves.new(nombre, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_mode = "OBJECT"
    cu.bevel_object = ob_p
    cu.use_fill_caps = True
    cu.resolution_u = 48
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(puntos) - 1)
    for bp, (co, giro, radio) in zip(sp.bezier_points, puntos):
        bp.co = co
        bp.handle_left_type = bp.handle_right_type = "AUTO"
        bp.tilt = giro
        bp.radius = radio
    ob = bpy.data.objects.new(nombre, cu)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def escena(args):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for tipo in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = tipo
            prefs.get_devices()
            if any(d.type == tipo for d in prefs.devices):
                for d in prefs.devices:
                    d.use = d.type == tipo
                sc.cycles.device = "GPU"
                break
        except TypeError:
            continue
    c = sc.cycles
    c.samples = args.muestras
    c.use_adaptive_sampling = True
    c.adaptive_threshold = 0.006
    c.use_denoising = True
    c.max_bounces, c.transmission_bounces, c.glossy_bounces, c.transparent_max_bounces = 24, 20, 10, 16
    c.caustics_reflective = c.caustics_refractive = True
    c.blur_glossy = 0.4
    c.sample_clamp_indirect = 12.0
    sc.render.resolution_x, sc.render.resolution_y = args.ancho, args.alto
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "AgX"
    deseado = "Medium High Contrast"
    for look in (f"AgX - {deseado}", deseado):
        try:
            sc.view_settings.look = look
            break
        except TypeError:
            continue
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_depth = "16"

    oscuro = args.modo == "oscuro"
    mundo = bpy.data.worlds.new("mundo")
    sc.world = mundo
    mundo.use_nodes = True
    fondo = mundo.node_tree.nodes["Background"]
    fondo.inputs["Color"].default_value = (0, 0, 0, 1) if oscuro else (0.80, 0.86, 0.93, 1)
    fondo.inputs["Strength"].default_value = 0.0 if oscuro else 0.9

    # ajolote de cristal, de frente (como el relieve del fondo de siempre)
    vidrio = cristal("cristal", tinte=(1.0, 0.985, 1.0) if oscuro else (0.95, 0.975, 1.0))
    aj = malla_ajolote(args.resolucion_forma)
    aj.data.materials.append(vidrio)
    aj.rotation_euler = (math.radians(90), 0, 0)
    aj.location = (0.0, 0.0, 0.3)

    # suelo bajo el ajolote: agua negra con reflejos de aceite (oscuro) o superficie clara pulida (claro)
    suelo = -2.05
    if args.solo_ajolote:
        sc.render.film_transparent = True
    elif oscuro:
        agua = superficie("agua", (0.003, 0.003, 0.005), 0.02, (160.0, 760.0))
        plano("agua", (80, 80), (0, 20, suelo), mat=agua, sub=10, ondas=0.45)
    else:
        lisa = superficie("superficie", (0.16, 0.24, 0.36), 0.025, (120.0, 360.0))
        plano("superficie", (80, 80), (0, 20, suelo), mat=lisa, sub=9, ondas=0.06)

    # Iluminación de estudio de vidrio: paneles de luz de color fuera de cámara (invisibles para ella,
    # visibles en reflejos y refracciones). El negro queda limpio y el color vive en el cristal y el agua.
    def panel(nombre, pos, rot, tam, color, fuerza):
        o = plano(nombre, tam, pos, rot=rot, mat=emisor_suave(nombre, color, fuerza))
        o.visible_camera = False
        o.visible_shadow = False
        return o

    r90 = math.radians(90)

    def solo_cristal(luz, *receptores):
        """Light linking: esta luz solo afecta (y solo se refleja) en estos objetos."""
        col = bpy.data.collections.new(luz.name + "-receptores")
        for r in receptores:
            col.objects.link(r)
        luz.light_linking.receiver_collection = col
        return luz
    if oscuro:
        panel("naranja", (-7.0, 0.5, 0.4), (0, r90, 0), (8, 5.0), (1.0, 0.36, 0.06), 22)
        panel("azul", (7.0, 0.8, 1.2), (0, -r90, 0), (8, 5.0), (0.06, 0.32, 1.0), 22)
        panel("morado", (0.0, 1.0, 7.0), (0, 0, 0), (10, 5), MORADO, 12)
        solo_cristal(panel("blanco", (-1.5, -6.0, 9.5), (math.radians(-35), 0, 0), (6, 2.0), (1, 1, 1), 12), aj)
        # detrás del ajolote, solo visible A TRAVÉS del cristal (la cámara no lo ve directamente):
        # el cuerpo se llena del degradado naranja → morado → azul de la imagen 2 y el fondo sigue negro
        for o in (panel("detras-naranja", (-2.6, 5.0, -0.9), (r90, 0, 0), (4.4, 3.0), (1.0, 0.34, 0.05), 2.4),
                  panel("detras-morado", (0.0, 5.4, 0.6), (r90, 0, 0), (4.0, 3.6), MORADO, 1.8),
                  panel("detras-azul", (2.8, 5.0, 2.2), (r90, 0, 0), (4.4, 3.0), (0.05, 0.30, 1.0), 2.4),
                  panel("detras-blanco", (0.6, 4.6, 3.2), (r90, 0, 0), (2.6, 0.6), (1, 1, 1), 7),
                  panel("detras-frio", (0.4, 6.0, 1.0), (r90, 0, 0), (6.0, 4.0), (0.75, 0.82, 1.0), 0.9)):
            o.visible_glossy = False
        # cúpula de color que SOLO se ve a través del cristal: el ajolote se llena de color (imagen 2)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=28, location=(0, 0, 0), segments=48, ring_count=24)
        cupula = bpy.context.object
        cupula.name = "cupula"
        cm = bpy.data.materials.new("cupula")
        cm.use_nodes = True
        nt = cm.node_tree
        nt.nodes.clear()
        coord = nodo(nt, "ShaderNodeTexCoord", -900, 0)
        sep = nodo(nt, "ShaderNodeSeparateXYZ", -700, 0)
        nt.links.new(coord.outputs["Object"], sep.inputs[0])
        diag = nodo(nt, "ShaderNodeMath", -500, 0)
        diag.operation = "ADD"
        nt.links.new(sep.outputs["X"], diag.inputs[0])
        nt.links.new(sep.outputs["Z"], diag.inputs[1])
        norm = nt.nodes.new("ShaderNodeMapRange")
        norm.location = (-320, 0)
        norm.inputs["From Min"].default_value, norm.inputs["From Max"].default_value = -30.0, 30.0
        nt.links.new(diag.outputs[0], norm.inputs["Value"])
        rampa = nt.nodes.new("ShaderNodeValToRGB")
        rampa.location = (-120, 0)
        els = rampa.color_ramp.elements
        els[0].position, els[0].color = 0.25, (1.0, 0.35, 0.06, 1)
        els[1].position, els[1].color = 0.78, (0.05, 0.32, 1.0, 1)
        els.new(0.42).color = (1.0, 0.25, 0.55, 1)
        els.new(0.55).color = MORADO + (1,)
        els.new(0.66).color = (0.85, 0.9, 1.0, 1)
        nt.links.new(norm.outputs["Result"], rampa.inputs["Fac"])
        e = nodo(nt, "ShaderNodeEmission", 120, 0, Strength=1.15)
        nt.links.new(rampa.outputs["Color"], e.inputs["Color"])
        sal = nodo(nt, "ShaderNodeOutputMaterial", 320, 0)
        nt.links.new(e.outputs[0], sal.inputs["Surface"])
        cupula.data.materials.append(cm)
        cupula.visible_camera = cupula.visible_glossy = cupula.visible_diffuse = False
        cupula.visible_shadow = cupula.visible_volume_scatter = False
        # cielo alto de bandas de aceite: el agua ondulada lo refleja en estelas irisadas (imagen 4)
        o = plano("cielo-agua", (70, 16), (0.0, 34.0, 9.0), rot=(math.radians(100), 0, 0), mat=aceite("aceite", 1.9))
        o.visible_camera = False
    else:
        cielo = bpy.data.materials.new("cielo")
        cielo.use_nodes = True
        nt = cielo.node_tree
        nt.nodes.clear()
        coord = nodo(nt, "ShaderNodeTexCoord", -900, 0)
        sep = nodo(nt, "ShaderNodeSeparateXYZ", -700, 0)
        nt.links.new(coord.outputs["Generated"], sep.inputs[0])
        rampa = nt.nodes.new("ShaderNodeValToRGB")
        rampa.location = (-450, 0)
        rampa.color_ramp.elements[0].color = (0.10, 0.20, 0.38, 1)
        rampa.color_ramp.elements[1].color = (0.98, 0.99, 1.0, 1)
        rampa.color_ramp.elements.new(0.40).color = (0.55, 0.68, 0.84, 1)
        rampa.color_ramp.elements.new(0.62).color = (0.90, 0.93, 0.97, 1)
        nt.links.new(sep.outputs["Y"], rampa.inputs["Fac"])
        em = nodo(nt, "ShaderNodeEmission", -100, 0, Strength=1.0)
        nt.links.new(rampa.outputs["Color"], em.inputs["Color"])
        sal = nodo(nt, "ShaderNodeOutputMaterial", 150, 0)
        nt.links.new(em.outputs[0], sal.inputs["Surface"])
        plano("cielo", (90, 40), (0, 22, 6), rot=(r90, 0, 0), mat=cielo)
        # el cristal de la imagen 1: reflejos azul profundo en las curvas y un arcoíris suave en el borde
        panel("azul-hondo", (0.0, 3.0, -1.9), (math.radians(20), 0, 0), (12, 4), (0.04, 0.16, 0.42), 9)
        panel("azul-lado", (7.0, 0.8, 1.0), (0, -r90, 0), (8, 5), (0.2, 0.46, 1.0), 12)
        panel("calido", (-7.0, 0.5, 0.5), (0, r90, 0), (8, 5), (1.0, 0.70, 0.42), 8)
        panel("blanco", (-1.5, -7.0, 5.5), (math.radians(-60), 0, 0), (6, 2.0), (1, 1, 1), 22)

    # luces para los brillos del cristal (no se ven directamente)
    if oscuro:
        solo_cristal(luz_area("borde", (5, 5, 3), (0, 0, 0.3), (1, 1, 1), 500, 2), aj)
    else:
        luz_area("sol", (-5, -6, 8), (0, 0, 0.3), (1.0, 0.98, 0.95), 2600, 3)
        luz_area("borde", (3, 7, 5), (0, 0, 0.3), (1, 1, 1), 700, 3)

    # cámara de frente, un poco desde arriba; el fondo queda desenfocado
    cam_d = bpy.data.cameras.new("cam")
    cam_d.lens = 88 if args.solo_ajolote else 50
    cam_d.dof.use_dof = True
    cam_d.dof.aperture_fstop = 0.13 if oscuro else 0.16   # la escena mide metros: así el fondo se desenfoca
    cam = bpy.data.objects.new("cam", cam_d)
    bpy.context.collection.objects.link(cam)
    # oscuro: desde arriba, todo el fondo es agua (sin horizonte, imagen 4); claro: casi de frente
    cam.location = (0.0, -11.3, 2.3) if oscuro else (0.0, -11.5, 1.0)
    objetivo = (0.0, 0.0, 0.05) if oscuro else (0.0, 0.0, 0.15)
    cam.rotation_euler = _mirar(np.array(objetivo) - np.array(cam.location))
    cam_d.dof.focus_distance = float(np.linalg.norm(np.array(objetivo) - np.array(cam.location)))
    sc.camera = cam
    return sc


def main():
    args = argumentos()
    sc = escena(args)
    sc.render.filepath = str(Path(args.salida).resolve())
    bpy.ops.render.render(write_still=True)
    print("FONDO", sc.render.filepath)


if __name__ == "__main__":
    main()
