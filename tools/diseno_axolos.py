#!/usr/bin/env python3
"""AxolOS · disposición del escritorio para los temas globales (oscuro y claro).

Plasma, al aplicar un tema global con «Diseño del escritorio y de las ventanas», BORRA los paneles y
widgets y ejecuta contents/layouts/org.kde.plasma.desktop-layout.js del tema; si el tema no lo trae,
pone el diseño de KDE (barra abajo con Kickoff). Este generador escribe ese guion a partir de la
disposición de AxolOS que reciben las cuentas nuevas (skel: plasma-org.kde.plasma.desktop-appletsrc
y plasmashellrc), así aplicar el tema deja exactamente el escritorio de AxolOS: barra arriba con menú
global, bandeja y reloj, y dock flotante de cristal con Bento y las apps ancladas.

Uso: tools/diseno_axolos.py
"""
import configparser
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SKEL = RAIZ / "packages/axolos-kde-settings/skel/.config"
TEMAS = RAIZ / "packages/axolos-themes/assets/plasma/look-and-feel"
RELOJ = RAIZ / "packages/axolos-kde-settings/plasma-updates/axolos-reloj-escritorio.js"
UBICACION = {"3": "top", "4": "bottom", "5": "left", "6": "right"}
LONGITUD = {"0": "fill", "1": "fit", "2": "custom"}
OCULTAR = {"0": "none", "1": "autohide", "2": "dodgewindows", "3": "windowsgobelow"}
OPACIDAD = {"0": "adaptive", "1": "opaque", "2": "translucent"}
INTERNO = {"popupHeight", "popupWidth", "favoritesPortedToKAstats", "favoritesSeeded", "migrated",
           "currentDetailsTab"}   # estado que Plasma guarda solo; no es configuración


def leer(ruta):
    """INI de KDE (grupos anidados «[a][b]») → {tupla de grupos: {clave: valor}}."""
    datos, grupo = {}, None
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if linea.startswith("["):
            grupo = tuple(re.findall(r"\[([^\]]*)\]", linea))
            datos.setdefault(grupo, {})
        elif grupo is not None and "=" in linea:
            k, v = linea.split("=", 1)
            datos[grupo][k] = v
    return datos


def js(v):
    return json.dumps(v, ensure_ascii=False)


def guion():
    a = leer(SKEL / "plasma-org.kde.plasma.desktop-appletsrc")
    s = leer(SKEL / "plasmashellrc")
    lineas = ["// AxolOS · disposición del escritorio (generado por tools/diseno_axolos.py desde skel; no editar a mano)",
              "// Plasma borra paneles y widgets y ejecuta esto al aplicar el tema con «Diseño del escritorio».", ""]
    # fondo de los escritorios
    imagen = next((v["Image"] for g, v in a.items() if g[-3:] == ("Wallpaper", "org.kde.image", "General")
                   and "Image" in v), None)
    if imagen:
        lineas += ["desktops().forEach(function (d) {",
                   '    d.wallpaperPlugin = "org.kde.image";',
                   '    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];',
                   f'    d.writeConfig("Image", {js(imagen)});',
                   "});", ""]
    # paneles, en el orden de skel
    for g, v in sorted(a.items(), key=lambda x: x[0]):
        if len(g) != 2 or g[0] != "Containments" or v.get("plugin") != "org.kde.panel":
            continue
        cid = g[1]
        vista = s.get(("PlasmaViews", f"Panel {cid}"), {})
        defectos = s.get(("PlasmaViews", f"Panel {cid}", "Defaults"), {})
        p = f"panel{cid}"
        lineas.append(f"var {p} = new Panel;")
        lineas.append(f'{p}.location = {js(UBICACION.get(v.get("location", "4"), "bottom"))};')
        if "thickness" in defectos:
            lineas.append(f"{p}.height = {int(defectos['thickness'])};")
        if "panelLengthMode" in vista:
            lineas.append(f"{p}.lengthMode = {js(LONGITUD[vista['panelLengthMode']])};")
        if "panelVisibility" in vista:
            lineas.append(f"{p}.hiding = {js(OCULTAR[vista['panelVisibility']])};")
        lineas.append(f"{p}.floating = {'true' if vista.get('floating', '1') == '1' else 'false'};")
        lineas.append(f"{p}.opacity = {js(OPACIDAD[vista.get('panelOpacity', '2')])};")
        orden = a.get(("Containments", cid, "General"), {}).get("AppletOrder", "")
        ids = [i for i in orden.split(";") if i] or sorted(
            {gg[3] for gg in a if len(gg) == 4 and gg[:3] == ("Containments", cid, "Applets")}, key=int)
        for aid in ids:
            plugin = a.get(("Containments", cid, "Applets", aid), {}).get("plugin")
            if not plugin:
                continue
            w = f"w{aid}"
            lineas.append(f"var {w} = {p}.addWidget({js(plugin)});")
            conf = a.get(("Containments", cid, "Applets", aid, "Configuration", "General"), {})
            conf = {k: val for k, val in conf.items() if k not in INTERNO}
            if conf:
                lineas.append(f'{w}.currentConfigGroup = ["General"];')
                for k, val in conf.items():
                    valor = val.split(",") if k == "launchers" else val
                    lineas.append(f"{w}.writeConfig({js(k)}, {js(valor)});")
        lineas.append("")
    # reloj analógico del escritorio, arriba a la derecha de la pantalla de cada uno (el mismo guion
    # que se ejecuta una vez en las cuentas nuevas)
    reloj = RELOJ.read_text(encoding="utf-8").strip()
    lineas += ["// reloj del escritorio", reloj, ""]
    return "\n".join(lineas)


def main():
    texto = guion()
    for tema in ("com.noel.axolos", "com.noel.axolos.claro"):
        destino = TEMAS / tema / "contents/layouts/org.kde.plasma.desktop-layout.js"
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8")
        print(destino)


if __name__ == "__main__":
    main()
