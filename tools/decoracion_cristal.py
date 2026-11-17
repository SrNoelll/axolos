#!/usr/bin/env python3
"""AxolOS · barras de título de cristal (Aurorae), oscura y clara, dibujadas desde cero.

  · la barra es el MISMO cristal que el cuerpo de la ventana: color y opacidad salen de Kvantum
    (tools/kvantum_axolos.py), así barra y contenido son una sola lámina, con foco y sin él
  · sin contorno ni filos: el borde lo marca el efecto Glass (refracción y luz en el canto)
  · esquinas de 14 px, las mismas que redondea el efecto Glass (TopCornerRadius/BottomCornerRadius)
  · sombra de verdad: desenfoque gaussiano de la forma redondeada (arriba y abajo), recortada bajo la
    ventana para que no la oscurezca; más marcada con foco
  · maximizada: barra recta, sin sombra
Los botones (close.svg, etc.: tools/botones_axolos.py) no se tocan.

Uso: tools/decoracion_cristal.py [carpeta aurorae/themes]
"""
import base64
import io
import json
import re
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kvantum_axolos  # noqa: E402  color y transparencia de las ventanas

TEMAS = Path(__file__).resolve().parent.parent / "packages/axolos-themes/assets/aurorae/themes"
R = 14                    # radio de las esquinas
TITULO = 32               # TitleEdgeTop + TitleHeight + TitleEdgeBottom
PL = PR = 44              # márgenes para la sombra
PT, PB = 28, 60
M = 16                    # pieza que se estira
SOMBRAS = {               # capas (sigma, desplazamiento vertical, opacidad)
    "": [(15.0, 9.0, 0.46), (3.0, 1.5, 0.20)],
    "-inactive": [(10.0, 5.0, 0.26), (2.0, 1.0, 0.10)],
}
VARIANTES = {
    "AxolOS": {"kvantum": "AxolOSDark", "texto": "236,236,243", "texto_inactivo": "138,138,153",
               "nombre": "AxolOS", "descripcion": "AxolOS liquid glass window decorations (dark)"},
    "AxolOS-Claro": {"kvantum": "AxolOS", "texto": "28,34,48", "texto_inactivo": "122,130,149",
                     "nombre": "AxolOS Claro", "descripcion": "AxolOS liquid glass window decorations (light)"},
}


def f(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")


def cobertura(ancho, alto, x0, y0, x1, y1, radio):
    """Rectángulo redondeado suavizado (1 dentro, 0 fuera) en una imagen ancho×alto."""
    yy, xx = np.mgrid[0:alto, 0:ancho] + 0.5
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    qx = np.abs(xx - cx) - ((x1 - x0) / 2 - radio)
    qy = np.abs(yy - cy) - ((y1 - y0) / 2 - radio)
    d = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - radio
    return np.clip(0.5 - d, 0, 1)


def desenfocar(a, sigma):
    fy = np.fft.fftfreq(a.shape[0])[:, None]
    fx = np.fft.rfftfreq(a.shape[1])[None, :]
    return np.fft.irfft2(np.fft.rfft2(a) * np.exp(-2 * (np.pi * sigma) ** 2 * (fx ** 2 + fy ** 2)), s=a.shape)


def sombra(ancho, alto, capas):
    """Alfa de la sombra del marco ancho×alto (la ventana ocupa el hueco entre los márgenes)."""
    m = 64                                               # margen para que el desenfoque no envuelva
    A, H = ancho + 2 * m, alto + 2 * m
    x0, y0, x1, y1 = PL + m, PT + m, ancho - PR + m, alto - PB + m
    total = np.zeros((H, A))
    for sigma, dy, opacidad in capas:
        forma = cobertura(A, H, x0, y0 + dy, x1, y1 + dy, R)
        total = 1 - (1 - total) * (1 - opacidad * np.clip(desenfocar(forma, sigma), 0, 1))
    total *= 1 - cobertura(A, H, x0, y0, x1, y1, R)        # nada bajo la ventana
    return total[m:m + alto, m:m + ancho]


def png(alfa):
    img = np.zeros(alfa.shape + (4,), np.uint8)
    img[..., 3] = np.round(np.clip(alfa, 0, 1) * 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(img, "RGBA").save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def marco(prefijo, ox, oy, color, opacidad, maximizada=False):
    """Las 9 piezas de un estado de la decoración. Devuelve (elementos, ancho, alto)."""
    if maximizada:
        pl = pr = pt = pb = 0
        xs, ys = [0, 8, 8 + M, 16 + M], [0, TITULO, TITULO + M, TITULO + M + 1]
    else:
        pl, pr, pt, pb = PL, PR, PT, PB
        xs = [0, PL + R, PL + R + M, 2 * (PL + R) + M]
        ys = [0, PT + TITULO, PT + TITULO + M, PT + TITULO + M + R + PB]
    ancho, alto = xs[-1], ys[-1]
    alfa = None if maximizada else sombra(ancho, alto, SOMBRAS["-inactive" if "inactive" in prefijo else ""])
    relleno = f'fill="{color}" fill-opacity="{f(opacidad)}"'
    x0, y0, x1, y1 = pl, pt, ancho - pr, pt + TITULO          # barra de título
    r = 0 if maximizada else R
    nombres = [["topleft", "top", "topright"], ["left", "center", "right"], ["bottomleft", "bottom", "bottomright"]]
    piezas = []
    for fi in range(3):
        for co in range(3):
            px0, py0, px1, py1 = xs[co], ys[fi], xs[co + 1], ys[fi + 1]
            dentro = [f'<rect x="{ox + px0}" y="{oy + py0}" width="{px1 - px0}" height="{py1 - py0}" '
                      f'fill="#000" fill-opacity="0.002"/>']           # fija los límites de la pieza
            if alfa is not None:
                dentro.append(f'<image x="{ox + px0}" y="{oy + py0}" width="{px1 - px0}" height="{py1 - py0}" '
                              f'preserveAspectRatio="none" href="data:image/png;base64,{png(alfa[py0:py1, px0:px1])}"/>')
            if fi == 0:                                       # la barra, en vector (nítida a cualquier escala)
                X0, X1 = max(px0, x0), min(px1, x1)
                if X1 > X0:
                    if co == 0 and r:
                        d = (f"M{ox + x0},{oy + y1} L{ox + x0},{oy + y0 + r} A{r},{r} 0 0 1 {ox + x0 + r},{oy + y0} "
                             f"L{ox + X1},{oy + y0} L{ox + X1},{oy + y1} Z")
                    elif co == 2 and r:
                        d = (f"M{ox + X0},{oy + y0} L{ox + x1 - r},{oy + y0} A{r},{r} 0 0 1 {ox + x1},{oy + y0 + r} "
                             f"L{ox + x1},{oy + y1} L{ox + X0},{oy + y1} Z")
                    else:
                        d = f"M{ox + X0},{oy + y0} L{ox + X1},{oy + y0} L{ox + X1},{oy + y1} L{ox + X0},{oy + y1} Z"
                    dentro.append(f'<path d="{d}" {relleno}/>')
            piezas.append(f'<g id="{prefijo}-{nombres[fi][co]}">{"".join(dentro)}</g>')
    return piezas, ancho, alto


def svg(color, opacidad):
    elementos, x, alto_max = [], 0, 0
    for prefijo, maxim in (("decoration", False), ("decoration-inactive", False),
                           ("decoration-maximized", True), ("decoration-maximized-inactive", True)):
        piezas, ancho, alto = marco(prefijo, x, 0, color, opacidad, maxim)
        elementos += piezas
        x += ancho + 20
        alto_max = max(alto_max, alto)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{x}" height="{alto_max}" '
            f'viewBox="0 0 {x} {alto_max}">\n' + "\n".join(elementos) + "\n</svg>\n")


def ajustar_rc(rc, v):
    valores = {"ActiveTextColor": v["texto"], "InactiveTextColor": v["texto_inactivo"], "UseTextShadow": "false",
               "Blur": "true", "Shadow": "true", "BorderLeft": "0", "BorderRight": "0", "BorderBottom": "0",
               "PaddingTop": str(PT), "PaddingBottom": str(PB), "PaddingLeft": str(PL), "PaddingRight": str(PR)}
    for clave, valor in valores.items():
        rc = re.sub(rf"^{clave}=.*$", f"{clave}={valor}", rc, flags=re.M)
    return rc


def main():
    temas = Path(sys.argv[1]) if len(sys.argv) > 1 else TEMAS
    base = temas / "AxolOS"
    rc_base = (base / "AxolOSrc").read_text(encoding="utf-8")
    meta_base = json.loads((base / "metadata.json").read_text(encoding="utf-8"))
    for nombre, v in VARIANTES.items():
        destino = temas / nombre
        if nombre != "AxolOS":
            shutil.rmtree(destino, ignore_errors=True)
            shutil.copytree(base, destino)
            (destino / "AxolOSrc").unlink()
        _, _, _, transparencia, colores = kvantum_axolos.VARIANTES[v["kvantum"]]
        (destino / "decoration.svg").write_text(svg(colores["window.color"], 1 - transparencia / 100),
                                                encoding="utf-8")
        (destino / f"{nombre}rc").write_text(ajustar_rc(rc_base, v), encoding="utf-8")
        meta = json.loads(json.dumps(meta_base))
        meta["KPlugin"].update({"Name": v["nombre"], "Id": nombre, "Description": v["descripcion"]})
        meta["X-KDE-PluginInfo-blur"] = meta["KPlugin"]["X-KDE-PluginInfo-blur"] = True
        (destino / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
        desk = destino / "metadata.desktop"
        if desk.exists():
            t = desk.read_text(encoding="utf-8")
            t = re.sub(r"^Name=.*$", f"Name={v['nombre']}", t, flags=re.M)
            t = re.sub(r"^X-KDE-PluginInfo-Name=.*$", f"X-KDE-PluginInfo-Name={nombre}", t, flags=re.M)
            desk.write_text(t, encoding="utf-8")
        print(destino)


if __name__ == "__main__":
    main()
