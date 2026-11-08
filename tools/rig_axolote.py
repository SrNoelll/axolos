#!/usr/bin/env python3
"""Rig del ajolote AxolOS: corta las piezas del ajolote REAL del fondo de pantalla.

Uso: rig_axolote.py FONDO.jpg SILUETA.png SALIDA_DIR

- SILUETA.png: logo recortado (631x495) alineado con el ajolote del fondo.
- Genera en SALIDA_DIR:
    core.png, tail.png, leg_fl.png, leg_fr.png, leg_bl.png, leg_br.png  (RGBA recortadas)
    plate.jpg   fondo completo con el hueco de patas/cola relleno (para cuando se mueven)
    hole.png    sombra suave del ajolote del fondo (fase oscura: ni silueta ni fantasma)
    rig.json    posiciones, pivotes y orden de capas (fuente única para el QML)
Coordenadas "u" = unidades del logo (0..10 en x e y, como la rejilla de la hoja).
"""
import json
import math
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# Ajolote dentro del fondo (px del fondo 2730x1536), medido por superposición
AX, AY, AW, AH = 296, 72, 1892, 1484

# Piezas: polígono en unidades del logo, pivote y si va delante o detrás del cuerpo
PARTS = {
    "tail":   {"z": -2, "pivot": (8.9, 1.9),
               "poly": [(8.3, 0.7), (10.3, 1.2), (10.4, 6.2), (9.4, 8.7), (7.6, 10.2), (5.25, 10.3),
                        (5.25, 9.05), (6.6, 8.0), (8.0, 6.8), (8.6, 5.2), (8.6, 3.0), (8.25, 2.3)]},
    "leg_fl": {"z": -1, "pivot": (1.45, 6.45),
               "poly": [(0.0, 6.0), (1.55, 5.9), (1.65, 7.2), (1.25, 8.4), (0.0, 8.2)]},
    "leg_bl": {"z": 1, "pivot": (6.55, 3.15),
               "poly": [(5.65, 3.4), (6.2, 2.95), (7.0, 3.0), (7.05, 4.0), (6.65, 5.2), (5.6, 5.2)]},
    "leg_br": {"z": 2, "pivot": (7.6, 2.5),
               "poly": [(7.05, 2.4), (8.0, 2.15), (8.42, 3.4), (8.15, 6.0), (7.0, 6.0), (7.15, 4.4)]},
    "leg_fr": {"z": 3, "pivot": (5.15, 6.05),
               "poly": [(4.4, 5.95), (5.7, 5.7), (5.95, 6.6), (5.65, 8.0), (5.2, 9.15), (3.85, 9.15),
                        (3.85, 7.6), (4.6, 7.2)]},
}
JOINT_R = 0.75      # radio (u) del relleno del cuerpo bajo cada articulación


def u2px(x, y):
    return (AX + x / 10.0 * AW, AY + y / 10.0 * AH)


def poly_mask(size, pts):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon([u2px(*p) for p in pts], fill=255)
    return np.asarray(m) > 127


def disk_mask(size, c, r_u):
    cx, cy = u2px(*c)
    r = r_u / 10.0 * AW
    yy, xx = np.mgrid[0:size[1], 0:size[0]]
    return (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r


def _resize_f(a, w, h):
    """Redimensiona un array float (H,W,3) con bilineal, canal a canal."""
    return np.dstack([np.asarray(Image.fromarray(a[..., c].astype(np.float32), "F").resize((w, h), Image.BILINEAR))
                      for c in range(a.shape[2])])


def fill(img, hole, known):
    """Reconstrucción push-pull: 'hole' se rellena SOLO a partir de 'known'
    (pirámide con medias ponderadas), sin rastro de lo que había debajo."""
    known = known & ~hole
    I = img.astype(np.float32) * known[..., None]
    Wt = known.astype(np.float32)
    pyr = []
    while min(I.shape[:2]) > 3:
        pyr.append((I, Wt))
        h, w = (I.shape[0] // 2) * 2, (I.shape[1] // 2) * 2
        I = I[:h, :w].reshape(h // 2, 2, w // 2, 2, 3).sum((1, 3))
        Wt = Wt[:h, :w].reshape(h // 2, 2, w // 2, 2).sum((1, 3))
    C = I / np.maximum(Wt, 1e-6)[..., None]
    for If, Wf in reversed(pyr):
        h, w = If.shape[:2]
        up = _resize_f(C, w, h)
        a = np.clip(Wf, 0, 1)[..., None]
        Cf = If / np.maximum(Wf, 1e-6)[..., None]
        C = a * Cf + (1 - a) * up
    out = img.astype(np.float32).copy()
    out[hole] = C[hole]
    return out


def bbox(mask, pad=4):
    ys, xs = np.nonzero(mask)
    return (max(xs.min() - pad, 0), max(ys.min() - pad, 0), xs.max() + pad + 1, ys.max() + pad + 1)


def main():
    wp_path, sil_path, out = sys.argv[1:4]
    wp = Image.open(wp_path).convert("RGB")
    size = wp.size
    rgb = np.asarray(wp, np.float32)

    # Silueta a escala del fondo
    sil = Image.open(sil_path).split()[-1].resize((AW, AH), Image.LANCZOS)
    full = Image.new("L", size, 0); full.paste(sil, (AX, AY))
    # Corte ceñido (ligeramente hacia dentro): sin halo del fondo alrededor
    sil_soft = full.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.6))
    sil_a = np.asarray(sil_soft, np.float32) / 255.0
    sil_b = sil_a > 0.5

    parts_mask = {}
    taken = np.zeros_like(sil_b)
    for name in sorted(PARTS, key=lambda n: -PARTS[n]["z"]):   # los de delante primero
        m = poly_mask(size, PARTS[name]["poly"]) & sil_b & ~taken
        parts_mask[name] = m
        taken |= m
    core_m = sil_b & ~taken

    rig = {"wallpaper": list(size), "axolotl": [AX, AY, AW, AH], "layers": []}

    # --- Cuerpo: relleno bajo cada articulación para que no se vea hueco al moverse
    core_rgb = rgb.copy()
    joint_fill = np.zeros_like(sil_b)
    for name, p in PARTS.items():
        joint_fill |= parts_mask[name] & disk_mask(size, p["pivot"], JOINT_R)
    core_rgb = fill(core_rgb, joint_fill, core_m)
    core_alpha = np.where(core_m | joint_fill, sil_a, 0.0)

    def save_layer(name, rgbarr, alpha, z, pivot=None):
        x0, y0, x1, y1 = bbox(alpha > 0.02)
        rgba = np.dstack([rgbarr[y0:y1, x0:x1], (alpha[y0:y1, x0:x1] * 255)]).clip(0, 255).astype(np.uint8)
        Image.fromarray(rgba, "RGBA").save(f"{out}/{name}.png", optimize=True)
        layer = {"name": name, "x": int(x0), "y": int(y0), "w": int(x1 - x0), "h": int(y1 - y0), "z": z}
        if pivot is not None:
            px, py = u2px(*pivot)
            layer["pivot"] = [round(px, 1), round(py, 1)]
        rig["layers"].append(layer)

    save_layer("core", core_rgb, core_alpha, 0)
    for name, p in PARTS.items():
        a = np.where(parts_mask[name], sil_a, 0.0)
        # suaviza el borde del corte para que la unión no se note
        a = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255.0
        a = np.minimum(a, sil_a)
        save_layer(name, rgb, a, p["z"], p["pivot"])

    # --- Fondo con patas y cola rellenadas (lo que se ve cuando se mueven)
    limb = np.asarray(Image.fromarray((taken * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(17))) > 0
    plate = fill(rgb, limb, ~limb)
    Image.fromarray(plate.clip(0, 255).astype(np.uint8)).save(f"{out}/plate.jpg", quality=92)

    # --- Sombra suave donde acabará el ajolote (fase oscura): oculta el ajolote
    # que ya está pintado en el fondo sin dejar una silueta reconocible
    hole = full.filter(ImageFilter.MaxFilter(41)).filter(ImageFilter.GaussianBlur(55))
    hole.resize((size[0] // 2, size[1] // 2), Image.BILINEAR).save(f"{out}/hole.png", optimize=True)

    rig["layers"].sort(key=lambda l: l["z"])
    with open(f"{out}/rig.json", "w") as f:
        json.dump(rig, f, indent=1)
    # el QML de KSplash no puede leer JSON de disco: lo mismo como módulo JS
    with open(f"{out}/rig.js", "w") as f:
        f.write(".pragma library\n// Generado por tools/rig_axolote.py — no editar a mano\nvar RIG = ")
        json.dump(rig, f)
        f.write(";\n")
    print(json.dumps(rig, indent=1))


if __name__ == "__main__":
    main()
