#!/usr/bin/env python3
"""Decoración de ventanas "AxolOS": MacTahoe-Dark con los botones en grafito
y el morado AxolOS al pasar el ratón; el de cerrar, siempre en morado
(en vez del semáforo rojo/amarillo/verde).

Uso: botones_axolos.py DIR_MacTahoe-Dark DIR_SALIDA
"""
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

TRAFFIC = {"#e9524a", "#f1ae1b", "#59c837", "#ed655a", "#e0443e", "#f5bf4f", "#61c554"}
STATE = {
    "active-center": "#5c5b67",          # en reposo: grafito
    "inactive-center": None,             # ventana sin foco: se queda gris como está
    "hover-center": "#a69afe",           # al pasar el ratón: morado AxolOS
    "hover-inactive-center": "#a69afe",
    "pressed-center": "#7662ce",         # al pulsar: morado oscuro
}
# El botón de cerrar va SIEMPRE en morado (petición de Noel)
CLOSE_STATE = {
    "active-center": "#a69afe",          # en reposo: morado AxolOS
    "inactive-center": "#8a80d6",        # ventana sin foco: morado algo más apagado
    "hover-center": "#cdc6ff",           # al pasar el ratón: se aclara
    "hover-inactive-center": "#cdc6ff",
    "pressed-center": "#7662ce",         # al pulsar: morado oscuro
}
HEX = re.compile(r"#[0-9a-fA-F]{6}")
ET.register_namespace("", "http://www.w3.org/2000/svg")
for p, u in [("inkscape", "http://www.inkscape.org/namespaces/inkscape"),
             ("sodipodi", "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"),
             ("xlink", "http://www.w3.org/1999/xlink"), ("dc", "http://purl.org/dc/elements/1.1/"),
             ("cc", "http://creativecommons.org/ns#"), ("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")]:
    ET.register_namespace(p, u)


def recolor(el, color, extra=()):
    targets = TRAFFIC | set(extra)
    for node in el.iter():
        for attr in ("style", "fill", "stroke"):
            v = node.get(attr)
            if v:
                node.set(attr, HEX.sub(lambda m: color if m.group(0).lower() in targets else m.group(0), v))


sys.path.insert(0, str(Path(__file__).resolve().parent))
from gtk_botones_axolos import COLORS as GTK_COLORS, svg as gtk_svg  # mismos dibujos en GTK y KWin

AURORAE_STATES = {"active-center": "normal", "hover-center": "hover", "pressed-center": "active",
                  "inactive-center": "backdrop-normal", "hover-inactive-center": "backdrop-hover",
                  "pressed-inactive-center": "backdrop-active", "deactivated-center": "backdrop-normal",
                  "deactivated-inactive-center": "backdrop-normal"}


def aurorae_button(btn, glyph):
    """SVG de botón para Aurorae: un grupo por estado (punto de 12 px + símbolo)."""
    parts = []
    for i, (gid, st) in enumerate(AURORAE_STATES.items()):
        inner = gtk_svg(GTK_COLORS[btn][st], glyph, st)
        inner = inner[inner.index(">") + 1: inner.rindex("</svg>")]
        op = ' opacity="0.5"' if gid.startswith("deactivated") else ""
        parts.append(f'<g id="{gid}" transform="translate({i * 20},0)"{op}>{inner}</g>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{len(AURORAE_STATES) * 20}" height="16" viewBox="0 0 {len(AURORAE_STATES) * 20} 16">'
            + "".join(parts) + "</svg>\n")


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(src, out)
    for svg in out.glob("*.svg"):
        if svg.name == "decoration.svg":
            continue
        tree = ET.parse(svg)
        states = CLOSE_STATE if svg.stem == "close" else STATE
        for el in tree.iter():
            color = states.get(el.get("id", ""))
            if color:
                # el de cerrar sin foco lleva un gris propio: también pasa a morado
                extra = ("#5d5d5d", "#666666") if svg.stem == "close" and el.get("id") == "inactive-center" else ()
                recolor(el, color, extra)
        tree.write(svg, xml_declaration=True, encoding="UTF-8")
    # Botones propios (mismos que en GTK): × − + y restaurar, finos sobre puntos de 12 px
    for name, btn, glyph in (("close", "close", "close"), ("minimize", "minimize", "minimize"),
                             ("maximize", "maximize", "maximize"), ("restore", "maximize", "maximized")):
        (out / f"{name}.svg").write_text(aurorae_button(btn, glyph), encoding="utf-8")
    rc = next(out.glob("*rc"))
    rc.rename(out / "AxolOSrc")
    for meta in ("metadata.desktop", "metadata.json"):
        f = out / meta
        if f.exists():
            t = f.read_text(encoding="utf-8")
            t = re.sub(r"MacTahoe-Dark", "AxolOS", t)
            f.write_text(t, encoding="utf-8")
    print("Decoración AxolOS creada en", out)


if __name__ == "__main__":
    main()
