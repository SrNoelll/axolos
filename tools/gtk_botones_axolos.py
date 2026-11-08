#!/usr/bin/env python3
"""Botones de ventana AxolOS para apps GTK3 / GTK4 (Brave, Chrome, Archivos…),
iguales que los de KWin: puntos finos de 12 px, sin contorno.

Uso: gtk_botones_axolos.py DIR_DIBUJOS DIR_CSS [RUTA_EN_EL_SISTEMA]
  DIR_DIBUJOS  carpeta (ruta absoluta) donde se escriben los SVG
  DIR_CSS      carpeta donde se escriben gtk3.css y gtk4.css (con rutas absolutas a los SVG)
  RUTA_EN_EL_SISTEMA  ruta que usará el CSS (para empaquetar; por defecto DIR_DIBUJOS)

(La conversión automática de KDE añade un contorno negro grueso y los hace
grandes; estos se dibujan a mano con los mismos colores que la decoración.)
"""
import sys
from pathlib import Path

DOT = 12          # diámetro del punto en KWin (lienzo de 16)
BOX = 16          # lienzo del dibujo
GTK_BOX = 16      # en apps GTK, el mismo tamaño que en KWin (así lo quiere Noel)
COLORS = {        # estado → color   (mismos que tools/botones_axolos.py)
    "close":    {"normal": "#a69afe", "hover": "#cdc6ff", "active": "#7662ce",
                 "backdrop-normal": "#a69afe", "backdrop-hover": "#cdc6ff", "backdrop-active": "#7662ce"},
    "minimize": {"normal": "#5c5b67", "hover": "#a69afe", "active": "#7662ce",
                 "backdrop-normal": "#5c5b67", "backdrop-hover": "#a69afe", "backdrop-active": "#7662ce"},
}
COLORS["maximize"] = COLORS["minimize"]
STATES = [("", "normal"), (":hover", "hover"), (":active", "active"),
          (":backdrop", "backdrop-normal"), (":backdrop:hover", "backdrop-hover"), (":backdrop:active", "backdrop-active")]


# Símbolo de cada botón (trazo fino y redondeado), en un lienzo de 16×16
GLYPHS = {
    "close":     "M5.75 5.75 L10.25 10.25 M10.25 5.75 L5.75 10.25",
    "minimize":  "M5.25 8 L10.75 8",
    "maximize":  "M8 5.25 L8 10.75 M5.25 8 L10.75 8",
    "maximized": "M6 7 L6 10 L9 10 M7 6 L10 6 L10 9",
}
DARK, LIGHT = "#241d4f", "#d6d6de"      # sobre morado · sobre grafito


def glyph_color(btn, st, fill):
    if fill == "#5c5b67":                        # grafito → símbolo claro
        return LIGHT, (0.55 if st.startswith("backdrop") else 0.9)
    return DARK, (0.6 if st.startswith("backdrop") else 0.85)


def svg(color, btn="close", st="normal", size=BOX):
    c = BOX / 2
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {BOX} {BOX}">'
            f'<circle cx="{c}" cy="{c}" r="{DOT / 2}" fill="{color}"/>')
    if st.endswith("normal"):                 # en reposo: solo el punto, sin símbolo
        return head + "</svg>\n"
    g, op = glyph_color(btn, st, color)
    return (head + f'<path d="{GLYPHS[btn]}" fill="none" stroke="{g}" stroke-opacity="{op}" stroke-width="1.35" '
            f'stroke-linecap="round" stroke-linejoin="round"/></svg>\n')


def main():
    art, cssdir = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
    base = sys.argv[3] if len(sys.argv) > 3 else str(art)
    art.mkdir(parents=True, exist_ok=True); cssdir.mkdir(parents=True, exist_ok=True)
    for btn, states in COLORS.items():
        for st, color in states.items():
            (art / f"{btn}-{st}.svg").write_text(svg(color, btn, st, GTK_BOX), encoding="utf-8")
            if btn == "maximize":       # ventana maximizada: símbolo de restaurar
                (art / f"maximized-{st}.svg").write_text(svg(color, "maximized", st, GTK_BOX), encoding="utf-8")
    common = (f"min-width: {GTK_BOX}px; min-height: {GTK_BOX}px; padding: 0; margin: 0 2px;"
              " border: none; border-radius: 50%; box-shadow: none; outline: none;"
              " background-color: transparent; background-repeat: no-repeat;"
              f" background-position: center; background-size: {GTK_BOX}px {GTK_BOX}px;")
    # GTK3 (Brave/Chrome en modo GTK, apps GTK3)
    g3 = ["/* AxolOS · botones de ventana GTK3 (iguales que los de KWin) */",
          f"headerbar button.titlebutton, .titlebar button.titlebutton {{ {common} }}",
          "headerbar .right > button.titlebutton + button.titlebutton { margin-left: 0; }",
          # El punto se pinta TAMBIÉN en el icono interior: el módulo de KDE
          # (window-decorations-gtk-module) tapa el fondo del botón con SVG vacíos
          # porque no sabe dibujar temas Aurorae, pero no toca el icono.
          "headerbar button.titlebutton image, .titlebar button.titlebutton image {"
          f" min-width: {GTK_BOX}px; min-height: {GTK_BOX}px; padding: 0; margin: 0; border: none; box-shadow: none;"
          " color: transparent; -gtk-icon-shadow: none; -gtk-icon-transform: scale(0);"
          f" background-color: transparent; background-repeat: no-repeat; background-position: center; background-size: {GTK_BOX}px {GTK_BOX}px; }}"]
    # GTK4 / libadwaita (Archivos…)
    g4 = ["/* AxolOS · botones de ventana GTK4/libadwaita (iguales que los de KWin) */",
          "windowcontrols { border-spacing: 2px; }",   # misma separación que en KWin (~20 px entre centros)
          f"windowcontrols > button {{ {common} }}",
          "windowcontrols > button > image { background: none; color: transparent; -gtk-icon-source: none; box-shadow: none;"
          " padding: 0; margin: 0; min-width: 0; min-height: 0; -gtk-icon-size: 0px; }"]
    for btn in COLORS:
        for sel, st in STATES:
            url = f'url("{base}/{btn}-{st}.svg")'
            g3.append(f"headerbar button.titlebutton.{btn}{sel}, .titlebar button.titlebutton.{btn}{sel}, "
                      f"headerbar button.titlebutton.{btn}{sel} image, .titlebar button.titlebutton.{btn}{sel} image "
                      f"{{ background-image: {url}; }}")
            g4.append(f"windowcontrols > button.{btn}{sel} {{ background-image: {url}; }}")
    for sel, st in STATES:
        url = f'url("{base}/maximized-{st}.svg")'
        g3.append(f".maximized headerbar button.titlebutton.maximize{sel}, .maximized .titlebar button.titlebutton.maximize{sel}, "
                  f".maximized headerbar button.titlebutton.maximize{sel} image, .maximized .titlebar button.titlebutton.maximize{sel} image "
                  f"{{ background-image: {url}; }}")
        g4.append(f"window.maximized windowcontrols > button.maximize{sel} {{ background-image: {url}; }}")
    (cssdir / "gtk3.css").write_text("\n".join(g3) + "\n", encoding="utf-8")
    (cssdir / "gtk4.css").write_text("\n".join(g4) + "\n", encoding="utf-8")
    print("Botones GTK AxolOS:", art, "·", cssdir)


if __name__ == "__main__":
    main()
