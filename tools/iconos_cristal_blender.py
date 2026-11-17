"""AxolOS · render de los iconos de cristal (lo lanza tools/iconos_cristal.py dentro de Blender).

  blender -b --factory-startup --python tools/iconos_cristal_blender.py -- trabajos.json MUESTRAS

Por icono: placa de color con capa de barniz (como un caramelo pulido) y, encima, el símbolo de
cristal con dispersión que la refracta. Cámara ortográfica cenital, fondo transparente, 512 px.
"""
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fondo_cristal as fc  # noqa: E402

ESCALA = 4.0      # el lienzo de 512 px mide 4 unidades


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple((int(h[i:i + 2], 16) / 255) ** 2.2 for i in (0, 2, 4))


def perfil_placa(m):
    """Placa con canto redondeado y cara superior plana."""
    u = fc.inflar(m)
    h = u / u.max()
    return np.clip(h / 0.32, 0, 1) ** 0.5


def placa_material(arriba, abajo):
    mat = bpy.data.materials.new("placa")
    mat.use_nodes = True
    nt = mat.node_tree
    p = nt.nodes["Principled BSDF"]
    coord = fc.nodo(nt, "ShaderNodeTexCoord", -900, 200)
    sep = fc.nodo(nt, "ShaderNodeSeparateXYZ", -700, 200)
    nt.links.new(coord.outputs["Generated"], sep.inputs[0])
    rampa = nt.nodes.new("ShaderNodeValToRGB")
    rampa.location = (-450, 200)
    rampa.color_ramp.elements[0].color = hex_rgb(abajo) + (1,)
    rampa.color_ramp.elements[1].color = hex_rgb(arriba) + (1,)
    nt.links.new(sep.outputs["Y"], rampa.inputs["Fac"])
    nt.links.new(rampa.outputs["Color"], p.inputs["Base Color"])
    nt.links.new(rampa.outputs["Color"], p.inputs["Emission Color"])
    p.inputs["Emission Strength"].default_value = 0.35
    p.inputs["Roughness"].default_value = 0.35
    p.inputs["Coat Weight"].default_value = 1.0
    p.inputs["Coat Roughness"].default_value = 0.04
    return mat


def esmerilado():
    """Cristal claro y luminoso para el símbolo: vidrio con dispersión + vidrio blanco esmerilado."""
    mat = fc.cristal("cristal", ior=1.5, dispersion=0.05, pelicula=(250.0, 600.0))
    nt = mat.node_tree
    salida = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    vidrio = salida.inputs["Surface"].links[0].from_node
    blanco = nt.nodes.new("ShaderNodeBsdfPrincipled")
    blanco.location = (500, -400)
    blanco.inputs["Base Color"].default_value = (1, 1, 1, 1)
    blanco.inputs["Roughness"].default_value = 0.28
    blanco.inputs["Transmission Weight"].default_value = 0.65
    blanco.inputs["Coat Weight"].default_value = 1.0
    blanco.inputs["Coat Roughness"].default_value = 0.02
    blanco.inputs["Emission Color"].default_value = (1, 1, 1, 1)
    blanco.inputs["Emission Strength"].default_value = 0.22
    mezcla = nt.nodes.new("ShaderNodeMixShader")
    mezcla.location = (750, 0)
    mezcla.inputs["Fac"].default_value = 0.5
    nt.links.new(vidrio.outputs[0], mezcla.inputs[1])
    nt.links.new(blanco.outputs[0], mezcla.inputs[2])
    nt.links.new(mezcla.outputs[0], salida.inputs["Surface"])
    return mat


def escena(muestras):
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
    c.samples = muestras
    c.use_denoising = True
    c.max_bounces, c.transmission_bounces, c.glossy_bounces = 16, 14, 8
    c.sample_clamp_indirect = 8.0
    sc.render.film_transparent = True
    sc.render.resolution_x = sc.render.resolution_y = 512
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "AgX"
    for look in ("AgX - Medium High Contrast", "Medium High Contrast"):
        try:
            sc.view_settings.look = look
            break
        except TypeError:
            continue
    mundo = bpy.data.worlds.new("mundo")
    sc.world = mundo
    mundo.use_nodes = True
    mundo.node_tree.nodes["Background"].inputs["Color"].default_value = (0.03, 0.03, 0.04, 1)
    mundo.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
    # estudio: paneles suaves que se reflejan en el barniz y en el cristal
    for nombre, pos, rot, tam, color, fuerza in (
            ("clave", (-3.0, 3.2, 5.5), (math.radians(-30), math.radians(-25), 0), (5, 3), (1, 1, 1), 14),
            ("borde", (3.5, -3.0, 3.0), (math.radians(40), math.radians(40), 0), (4, 1.2), (0.75, 0.82, 1.0), 8),
            ("calido", (-4.5, -2.0, 2.0), (math.radians(30), math.radians(-60), 0), (3, 1.0), (1.0, 0.72, 0.5), 5)):
        o = fc.plano(nombre, tam, pos, rot=rot, mat=fc.emisor_suave(nombre, color, fuerza))
        o.visible_camera = False
    luz = bpy.data.lights.new("sol", "AREA")
    luz.energy, luz.size = 260, 3
    ob = bpy.data.objects.new("sol", luz)
    bpy.context.collection.objects.link(ob)
    ob.location = (-2.5, 2.5, 6)
    ob.rotation_euler = fc._mirar(np.array((0, 0, 0)) - np.array(ob.location))
    ob.visible_camera = False
    cam_d = bpy.data.cameras.new("cam")
    cam_d.type = "ORTHO"
    cam_d.ortho_scale = ESCALA
    cam = bpy.data.objects.new("cam", cam_d)
    bpy.context.collection.objects.link(cam)
    cam.location = (0, 0, 10)
    sc.camera = cam
    return sc


def icono(t, muestras):
    sc = escena(muestras)
    placa = np.load(t["placa"])
    simbolo = np.load(t["simbolo"])
    arriba, abajo = t["colores"]
    p = fc.malla(placa, perfil_placa(placa), ESCALA, grosor=0.16, fondo=0.4, nombre="placa", suavizar=6)
    p.data.materials.append(placa_material(arriba, abajo))
    if simbolo.any():
        h = fc.inflar(simbolo)
        s = fc.malla(simbolo, h / h.max(), ESCALA, grosor=0.30, fondo=0.25, nombre="simbolo", suavizar=6)
        s.location.z = 0.17
        s.data.materials.append(esmerilado())
    sc.render.filepath = t["salida"]
    bpy.ops.render.render(write_still=True)


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    trabajos = json.loads(Path(args[0]).read_text())
    muestras = int(args[1]) if len(args) > 1 else 256
    for t in trabajos:
        icono(t, muestras)
        print("ICONO", t["nombre"])


if __name__ == "__main__":
    main()
