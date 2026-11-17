#!/usr/bin/env python3
"""AxolOS · marcos de cristal del tema de Plasma (paneles, menús emergentes, avisos y widgets).

Genera los SVG de 9 piezas (FrameSvg) que dibuja Plasma; el efecto Glass de KWin pone detrás el
desenfoque, la refracción y el irisado. Aquí va lo que es del tema:
  · relleno translúcido del color del esquema (ColorScheme-Background): sirve en claro y en oscuro
  · filo de luz de 1 px (más intenso arriba, se apaga hacia abajo) y un contorno fino exterior
  · un brillo muy suave en el borde superior
  · máscara (mask-*) con la misma forma: es la región que desenfoca y refracta KWin
  · sombra suave con degradados (QtSvg no admite filtros)
Variantes (así las elige Plasma): translucent/ cuando hay desenfoque detrás (con el cristal de KWin:
relleno muy ligero para que se vea la refracción), normal cuando no lo hay (más opaco, para leerse
sobre lo que haya detrás) y solid/ sin composición.

Uso: tools/plasma_cristal.py [carpeta del tema]   (por defecto, el tema AxolOS del paquete)
"""
import gzip
import sys
from pathlib import Path

TEMA = Path(__file__).resolve().parent.parent / "packages/axolos-themes/assets/plasma/desktoptheme/AxolOS"

ESTILO = """<style type="text/css" id="current-color-scheme">
.ColorScheme-Background { color:#17171d; }
.ColorScheme-Text { color:#e6e6ee; }
</style>"""

# marco: (archivo, radio, opacidad del relleno [normal = sin desenfoque, translucent = con cristal, sólido],
#         sombra, margen de contenido, prefijos)
MARCOS = [
    ("dialogs/background", 14, (0.86, 0.21, 0.97), 22, 10, ("",)),
    ("widgets/tooltip", 11, (0.88, 0.25, 0.97), 16, 8, ("",)),
    ("widgets/panel-background", 18, (0.84, 0.17, 0.97), 18, 6, ("", "north-", "south-", "west-", "east-")),
    ("widgets/background", 18, (0.82, 0.18, 0.96), 18, 12, ("",)),
    ("widgets/translucentbackground", 18, (0.62, 0.11, 0.92), 0, 12, ("",)),
]


def f(x):
    return f"{x:.3f}".rstrip("0").rstrip(".")


class Lienzo:
    """Acumula elementos con id; cada pieza se coloca en su propia celda (los ids marcan los límites)."""

    def __init__(self):
        self.defs, self.cuerpo, self.n = [], [], 0

    def grad(self, x1, y1, x2, y2, paradas):
        self.n += 1
        gid = f"g{self.n}"
        stops = "".join(f'<stop offset="{f(o)}" stop-color="{c}" stop-opacity="{f(a)}"/>' for o, c, a in paradas)
        self.defs.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{f(x1)}" y1="{f(y1)}" '
                         f'x2="{f(x2)}" y2="{f(y2)}">{stops}</linearGradient>')
        return f"url(#{gid})"

    def radial(self, cx, cy, r, paradas):
        self.n += 1
        gid = f"g{self.n}"
        stops = "".join(f'<stop offset="{f(o)}" stop-color="{c}" stop-opacity="{f(a)}"/>' for o, c, a in paradas)
        self.defs.append(f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="{f(cx)}" cy="{f(cy)}" '
                         f'r="{f(r)}">{stops}</radialGradient>')
        return f"url(#{gid})"

    def grupo(self, eid, x, y, w, h, formas):
        # rectángulo casi invisible: fija los límites exactos de la pieza
        caja = f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" fill="#000" fill-opacity="0.004"/>'
        self.cuerpo.append(f'<g id="{eid}">{caja}{"".join(formas)}</g>')

    def svg(self, ancho, alto):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}">'
                f'<defs>{ESTILO}{"".join(self.defs)}</defs>{"".join(self.cuerpo)}</svg>')


def cuarto(cx, cy, r, esquina):
    """Camino del cuarto de círculo relleno de una esquina (centro cx, cy)."""
    dx, dy = {"tl": (-1, -1), "tr": (1, -1), "bl": (-1, 1), "br": (1, 1)}[esquina]
    x0, y0 = cx + dx * r, cy
    x1, y1 = cx, cy + dy * r
    barrido = 1 if (dx * dy) > 0 else 0   # sentido horario en pantalla = curva hacia fuera
    return f"M{f(cx)},{f(cy)} L{f(x0)},{f(y0)} A{f(r)},{f(r)} 0 0 {barrido} {f(x1)},{f(y1)} Z"


def anillo(cx, cy, r_ext, r_int, esquina):
    """Cuarto de anillo relleno entre r_int y r_ext (un filo curvo sin trazo: límites exactos)."""
    dx, dy = {"tl": (-1, -1), "tr": (1, -1), "bl": (-1, 1), "br": (1, 1)}[esquina]
    b = 1 if (dx * dy) > 0 else 0
    return (f"M{f(cx + dx * r_ext)},{f(cy)} A{f(r_ext)},{f(r_ext)} 0 0 {b} {f(cx)},{f(cy + dy * r_ext)} "
            f"L{f(cx)},{f(cy + dy * r_int)} A{f(r_int)},{f(r_int)} 0 0 {1 - b} {f(cx + dx * r_int)},{f(cy)} Z")


def marco(L, ox, oy, prefijo, radio, opac, sombra, margen, mascara=True):
    """Las 9 piezas de un marco (y su máscara y sombra) a partir de (ox, oy). Devuelve el alto usado."""
    c, m = radio, 8             # tamaño de esquina y de las piezas que se estiran
    fondo = 'class="ColorScheme-Background" style="fill:currentColor;fill-opacity:%s"' % f(opac)
    filo_arriba, filo_abajo, contorno = 0.34, 0.07, 0.22
    celdas = {   # pieza: (x, y, w, h) relativos
        "topleft": (0, 0, c, c), "top": (c, 0, m, c), "topright": (c + m, 0, c, c),
        "left": (0, c, c, m), "center": (c, c, m, m), "right": (c + m, c, c, m),
        "bottomleft": (0, c + m, c, c), "bottom": (c, c + m, m, c), "bottomright": (c + m, c + m, c, c),
    }

    def pieza(nombre, x, y, w, h, extra_fondo=None):
        X, Y = ox + x, oy + y
        formas = []
        cx_, cy_ = None, None
        if nombre in ("topleft", "topright", "bottomleft", "bottomright"):
            esq = {"topleft": "tl", "topright": "tr", "bottomleft": "bl", "bottomright": "br"}[nombre]
            cx_ = X + (w if esq in ("tl", "bl") else 0)
            cy_ = Y + (h if esq in ("tl", "tr") else 0)
            formas.append(f'<path d="{cuarto(cx_, cy_, c, esq)}" {fondo}/>')
            if esq in ("tl", "tr"):   # brillo suave arriba
                g = L.grad(X, Y, X, Y + h, [(0, "#ffffff", 0.10), (1, "#ffffff", 0)])
                formas.append(f'<path d="{cuarto(cx_, cy_, c, esq)}" fill="{g}"/>')
            a_ext = filo_arriba if esq in ("tl", "tr") else filo_abajo
            formas.append(f'<path d="{anillo(cx_, cy_, c - 1.0, c - 2.0, esq)}" fill="#ffffff" '
                          f'fill-opacity="{f(a_ext)}"/>')
            formas.append(f'<path d="{anillo(cx_, cy_, c, c - 1.0, esq)}" fill="#000000" '
                          f'fill-opacity="{f(contorno)}"/>')
        else:
            formas.append(f'<rect x="{f(X)}" y="{f(Y)}" width="{f(w)}" height="{f(h)}" {fondo}/>')
            if nombre == "top":
                g = L.grad(X, Y, X, Y + h, [(0, "#ffffff", 0.10), (1, "#ffffff", 0)])
                formas.append(f'<rect x="{f(X)}" y="{f(Y)}" width="{f(w)}" height="{f(h)}" fill="{g}"/>')
                formas.append(f'<rect x="{f(X)}" y="{f(Y + 1)}" width="{f(w)}" height="1" fill="#ffffff" fill-opacity="{f(filo_arriba)}"/>')
                formas.append(f'<rect x="{f(X)}" y="{f(Y)}" width="{f(w)}" height="1" fill="#000" fill-opacity="{f(contorno)}"/>')
            elif nombre == "bottom":
                formas.append(f'<rect x="{f(X)}" y="{f(Y + h - 2)}" width="{f(w)}" height="1" fill="#ffffff" fill-opacity="{f(filo_abajo)}"/>')
                formas.append(f'<rect x="{f(X)}" y="{f(Y + h - 1)}" width="{f(w)}" height="1" fill="#000" fill-opacity="{f(contorno)}"/>')
            elif nombre in ("left", "right"):
                xr = X + 1 if nombre == "left" else X + w - 2
                xc = X if nombre == "left" else X + w - 1
                g = L.grad(X, Y, X, Y + h, [(0, "#ffffff", filo_arriba * 0.8), (1, "#ffffff", filo_abajo)])
                formas.append(f'<rect x="{f(xr)}" y="{f(Y)}" width="1" height="{f(h)}" fill="{g}"/>')
                formas.append(f'<rect x="{f(xc)}" y="{f(Y)}" width="1" height="{f(h)}" fill="#000" fill-opacity="{f(contorno)}"/>')
        L.grupo(prefijo + nombre, X, Y, w, h, formas)

    for nombre, (x, y, w, h) in celdas.items():
        pieza(nombre, x, y, w, h)

    alto = 2 * c + m + 6
    if mascara:   # misma forma, opaca: la región del cristal
        my = oy + alto
        for nombre, (x, y, w, h) in celdas.items():
            X, Y = ox + x, my + y
            if nombre in ("topleft", "topright", "bottomleft", "bottomright"):
                esq = {"topleft": "tl", "topright": "tr", "bottomleft": "bl", "bottomright": "br"}[nombre]
                cx_ = X + (w if esq in ("tl", "bl") else 0)
                cy_ = Y + (h if esq in ("tl", "tr") else 0)
                forma = f'<path d="{cuarto(cx_, cy_, c, esq)}" fill="#000"/>'
            else:
                forma = f'<rect x="{f(X)}" y="{f(Y)}" width="{f(w)}" height="{f(h)}" fill="#000"/>'
            L.grupo(prefijo + "mask-" + nombre, X, Y, w, h, [forma])
        alto += 2 * c + m + 6

    if sombra:    # sombra: degradados que se apagan hacia fuera
        s = sombra
        sy = oy + alto
        sc = {"topleft": (0, 0, s, s), "top": (s, 0, m, s), "topright": (s + m, 0, s, s),
              "left": (0, s, s, m), "right": (s + m, s, s, m),
              "bottomleft": (0, s + m, s, s), "bottom": (s, s + m, m, s), "bottomright": (s + m, s + m, s, s)}
        tono = [(0, "#000000", 0.30), (0.45, "#000000", 0.12), (1, "#000000", 0)]
        for nombre, (x, y, w, h) in sc.items():
            X, Y = ox + x, sy + y
            if nombre == "top":
                g = L.grad(X, Y + h, X, Y, tono)
            elif nombre == "bottom":
                g = L.grad(X, Y, X, Y + h, tono)
            elif nombre == "left":
                g = L.grad(X + w, Y, X, Y, tono)
            elif nombre == "right":
                g = L.grad(X, Y, X + w, Y, tono)
            else:
                cx_ = X + (w if "left" in nombre else 0)
                cy_ = Y + (h if "top" in nombre else 0)
                g = L.radial(cx_, cy_, s, tono)
            L.grupo(prefijo + "shadow-" + nombre, X, Y, w, h,
                    [f'<rect x="{f(X)}" y="{f(Y)}" width="{f(w)}" height="{f(h)}" fill="{g}"/>'])
        for lado, tam in (("top", s), ("bottom", s), ("left", s), ("right", s)):
            ancho_h, alto_h = (tam, 1) if lado in ("left", "right") else (1, tam)
            L.grupo(f"{prefijo}shadow-hint-{lado}-margin", ox, sy + 3 * s, ancho_h, alto_h, [])
        alto += 2 * s + m + 6 + 3 * s

    # márgenes del contenido
    hy = oy + alto
    for lado in ("top", "bottom", "left", "right"):
        ancho_h, alto_h = (margen, 1) if lado in ("left", "right") else (1, margen)
        L.grupo(f"{prefijo}hint-{lado}-margin", ox, hy, ancho_h, alto_h, [])
    return alto + margen + 8


def generar(tema):
    for archivo, radio, opacidades, sombra, margen, prefijos in MARCOS:
        for carpeta, opac in zip(("", "translucent/", "solid/"), opacidades):
            L = Lienzo()
            ox = 0
            for p in prefijos:
                marco(L, ox, 0, p, radio, opac, sombra if carpeta != "solid/" else max(sombra // 2, 0) or 0, margen)
                ox += 2 * max(radio, sombra) + 40
            destino = tema / carpeta / f"{archivo}.svgz"
            destino.parent.mkdir(parents=True, exist_ok=True)
            # mtime=0: el mismo SVG da el mismo .svgz (si no, cada ejecución «cambia» el paquete)
            with open(destino, "wb") as crudo, gzip.GzipFile(fileobj=crudo, mode="wb", compresslevel=9, mtime=0) as z:
                z.write(L.svg(ox + 10, 520).encode("utf-8"))
            print(destino.relative_to(tema))


if __name__ == "__main__":
    generar(Path(sys.argv[1]) if len(sys.argv) > 1 else TEMA)
