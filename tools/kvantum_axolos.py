#!/usr/bin/env python3
"""Crea el tema Kvantum «AxolOS» de cristal líquido, en claro y en oscuro, a partir de MacTahoe.

Uso: kvantum_axolos.py DIR_MacTahoe DIR_SALIDA

  AxolOS      (estilo «kvantum»)      ← MacTahoe.svg/.kvconfig       claro: blanco azulado (imagen 1)
  AxolOSDark  (estilo «kvantum-dark») ← MacTahoeDark.svg/.kvconfig   oscuro: negro violáceo (imágenes 2 y 4)

- Los azules del tema (tono 190°–245°, saturados) pasan al morado de AxolOS conservando su
  luminosidad y saturación: así se mantienen los contrastes del original.
- Los grises neutros toman el matiz del cristal (violeta azulado de noche, azul pálido de día).
- Cristal: ventanas y menús translúcidos con desenfoque en TODAS las ventanas (no solo la activa);
  el efecto Glass de KWin pone detrás la refracción y el irisado.
"""
import colorsys
import re
import sys
from pathlib import Path

HEX = re.compile(r"#([0-9a-fA-F]{6})\b")
MORADO_HUE = 250 / 360.0

VARIANTES = {
    # nombre: (origen, morado de destacado, matiz y saturación de los grises, transparencia de ventana %
    #         (deja ver el cristal de KWin detrás; el contenido —listas, texto— sigue opaco), colores)
    "AxolOS": ("MacTahoe", "#7662ce", (214 / 360, 0.22), 28, {
        "window.color": "#eef2f7", "inactive.window.color": "#eef2f7", "base.color": "#f8fafc",
        "inactive.base.color": "#f8fafc", "alt.base.color": "#f1f4f8", "inactive.alt.base.color": "#f1f4f8",
        "button.color": "#e3e9f1", "light.color": "#ffffff", "mid.light.color": "#e9eef5", "dark.color": "#b8c2d0",
        "mid.color": "#d3dbe6", "text.color": "#1c2230", "inactive.text.color": "#4a5366",
        "window.text.color": "#1c2230", "inactive.window.text.color": "#4a5366", "button.text.color": "#1c2230",
        "disabled.text.color": "#8a93a6", "tooltip.base.color": "#f6f8fb", "tooltip.text.color": "#1c2230",
        "highlight.text.color": "#ffffff", "inactive.highlight.text.color": "#ffffff",
        "link.color": "#6a55d8", "link.visited.color": "#8b6ad8", "progress.indicator.text.color": "#ffffff"}),
    "AxolOSDark": ("MacTahoeDark", "#a69afe", (245 / 360, 0.10), 34, {
        "window.color": "#121218", "inactive.window.color": "#121218", "base.color": "#0e0e13",
        "inactive.base.color": "#0e0e13", "alt.base.color": "#15151c", "inactive.alt.base.color": "#15151c",
        "button.color": "#24242e", "light.color": "#3a3a48", "mid.light.color": "#2e2e3a", "dark.color": "#0a0a0e",
        "mid.color": "#1d1d26", "text.color": "#ececf3", "inactive.text.color": "#b4b4c2",
        "window.text.color": "#ececf3", "inactive.window.text.color": "#b4b4c2", "button.text.color": "#ececf3",
        "disabled.text.color": "#6e6e80", "tooltip.base.color": "#17171f", "tooltip.text.color": "#ececf3",
        "highlight.text.color": "#ffffff", "inactive.highlight.text.color": "#ffffff",
        "link.color": "#a69afe", "link.visited.color": "#cdc6ff", "progress.indicator.text.color": "#ffffff"}),
}

CRISTAL = {   # [%General]
    "translucent_windows": "true", "blurring": "true", "popup_blurring": "true",
    "blur_only_active_window": "false", "reduce_menu_opacity": "30", "menu_blur_radius": "9",
    "tooltip_blur_radius": "6", "composite": "true",
    # la vista de archivos de Dolphin también de cristal, como la terminal (era opaca)
    "transparent_dolphin_view": "true",
}


def recolorear(texto, gris, oscuro):
    hue_g, sat_g = gris

    def cambio(m):
        h = m.group(1)
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
        if 190 / 360 <= hh <= 245 / 360 and ss > 0.25 and 0.08 < ll < 0.95:
            if oscuro:   # más claro, hacia #A69AFE
                ll = ll + (0.72 - ll) * 0.45 if ll < 0.72 else ll
            else:        # más hondo, hacia #7662CE (contraste sobre blanco)
                ll = ll + (0.60 - ll) * 0.4
            r, g, b = colorsys.hls_to_rgb(MORADO_HUE, ll, min(1.0, ss))
        elif ss < 0.06 and 0.04 < ll < 0.985:   # gris neutro → tinte del cristal
            s = sat_g if (oscuro or ll > 0.6) else sat_g * 0.5
            r, g, b = colorsys.hls_to_rgb(hue_g, ll, s)
        else:
            return m.group(0)
        return "#%02x%02x%02x" % tuple(round(c * 255) for c in (r, g, b))

    return HEX.sub(cambio, texto)


def ajustar(cfg, destacado, opacidad, colores):
    for k, v in {**CRISTAL, "reduce_window_opacity": str(opacidad)}.items():
        if re.search(rf"^{k}=", cfg, flags=re.M):
            cfg = re.sub(rf"^{k}=.*$", f"{k}={v}", cfg, flags=re.M)
        else:
            cfg = cfg.replace("[%General]\n", f"[%General]\n{k}={v}\n", 1)
    colores = {**colores, "highlight.color": destacado, "inactive.highlight.color": destacado}
    for k, v in colores.items():
        cfg = re.sub(rf"^{re.escape(k)}=.*$", f"{k}={v}", cfg, flags=re.M)
    return cfg.replace("comment=A dark theme with translucency similar to the style of macOS",
                       "comment=AxolOS liquid glass (from MacTahoe by Vince Liuice)")


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    for nombre, (origen, destacado, gris, opacidad, colores) in VARIANTES.items():
        oscuro = nombre.endswith("Dark")
        svg = recolorear((src / f"{origen}.svg").read_text(encoding="utf-8"), gris, oscuro)
        cfg = recolorear((src / f"{origen}.kvconfig").read_text(encoding="utf-8"), gris, oscuro)
        (out / f"{nombre}.svg").write_text(svg, encoding="utf-8")
        (out / f"{nombre}.kvconfig").write_text(ajustar(cfg, destacado, opacidad, colores), encoding="utf-8")
        print(f"{nombre}: {origen} → {out / nombre}.*")


if __name__ == "__main__":
    main()
