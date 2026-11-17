#!/usr/bin/env python3
"""AxolOS · esquemas de color de cristal líquido para KDE (claro y oscuro).

  AxolOSCristalOscuro.colors  (por defecto) negro violáceo de las imágenes 2 y 4
  AxolOSCristalClaro.colors   blanco azulado pálido de la imagen 1

Mismo morado de AxolOS (#A69AFE en oscuro, #7662CE en claro, más hondo para contrastar sobre blanco).
Uso: tools/colores_cristal.py [carpeta de salida]
"""
import sys
from pathlib import Path

SALIDA = Path(__file__).resolve().parent.parent / "packages/axolos-themes/assets/color-schemes"


def rgb(h):
    h = h.lstrip("#")
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


ESQUEMAS = {
    "AxolOSCristalOscuro": {
        "nombres": {"": "AxolOS Glass Dark", "es": "AxolOS Cristal oscuro", "fr": "AxolOS Verre sombre",
                    "ru": "AxolOS Стекло тёмное", "zh_CN": "AxolOS 玻璃 深色", "ja": "AxolOS ガラス ダーク"},
        "fondos": {"Window": ("#121218", "#16161d"), "View": ("#0e0e13", "#15151c"), "Button": ("#24242e", "#2b2b37"),
                   "Tooltip": ("#17171f", "#1d1d26"), "Header": ("#15151c", "#1a1a22"),
                   "Complementary": ("#0b0b10", "#121218"), "Selection": ("#7662ce", "#6a57c2")},
        "texto": "#ececf3", "inactivo": "#8a8a99", "acento": "#a69afe", "acento_hover": "#cdc6ff",
        "enlace": "#a69afe", "visitado": "#cdc6ff", "negativo": "#ff7a93", "neutro": "#f3cf7a", "positivo": "#7ddfb4",
        "wm": ("#15151c", "#ececf3", "#121218", "#8a8a99"),
    },
    "AxolOSCristalClaro": {
        "nombres": {"": "AxolOS Glass Light", "es": "AxolOS Cristal claro", "fr": "AxolOS Verre clair",
                    "ru": "AxolOS Стекло светлое", "zh_CN": "AxolOS 玻璃 浅色", "ja": "AxolOS ガラス ライト"},
        "fondos": {"Window": ("#eef2f7", "#e7ecf3"), "View": ("#f8fafc", "#f1f4f8"), "Button": ("#e3e9f1", "#dbe2ec"),
                   "Tooltip": ("#f6f8fb", "#eef2f7"), "Header": ("#e8edf4", "#e1e7f0"),
                   "Complementary": ("#1b2029", "#232935"), "Selection": ("#7662ce", "#6a57c2")},
        "texto": "#1c2230", "inactivo": "#6b7488", "acento": "#7662ce", "acento_hover": "#8b7de0",
        "enlace": "#6a55d8", "visitado": "#8b6ad8", "negativo": "#d6365a", "neutro": "#b07d00", "positivo": "#1e9e6a",
        "wm": ("#e8edf4", "#1c2230", "#eef2f7", "#7a8295"),
    },
}


def esquema(clave, e):
    oscuro = clave.endswith("Oscuro")
    lin = ["[General]", f"ColorScheme={clave}"]
    lin += [f"Name{f'[{l}]' if l else ''}={n}" for l, n in e["nombres"].items()]
    lin += ["", "[KDE]", "contrast=4", ""]
    lin += ["[ColorEffects:Disabled]", "Color=112,111,110", "ColorAmount=0", "ColorEffect=0",
            "ContrastAmount=0.65", "ContrastEffect=1", "IntensityAmount=0.1", "IntensityEffect=2", ""]
    lin += ["[ColorEffects:Inactive]", "ChangeSelectionColor=true", "Color=112,111,110", "ColorAmount=0.025",
            "ColorEffect=2", "ContrastAmount=0.1", "ContrastEffect=2", "Enable=false", "IntensityAmount=0",
            "IntensityEffect=0", ""]
    for grupo, (normal, alterno) in e["fondos"].items():
        comp = grupo == "Complementary"
        texto = "#ececf3" if (comp or grupo == "Selection") else e["texto"]
        if grupo == "Selection":
            texto = "#ffffff"
        lin += [f"[Colors:{grupo}]", f"BackgroundAlternate={rgb(alterno)}", f"BackgroundNormal={rgb(normal)}",
                f"DecorationFocus={rgb(e['acento'])}", f"DecorationHover={rgb(e['acento_hover'])}",
                f"ForegroundActive={rgb(e['acento'])}", f"ForegroundInactive={rgb(e['inactivo'] if not comp else '#8a8a99')}",
                f"ForegroundLink={rgb(e['enlace'])}", f"ForegroundNegative={rgb(e['negativo'])}",
                f"ForegroundNeutral={rgb(e['neutro'])}", f"ForegroundNormal={rgb(texto)}",
                f"ForegroundPositive={rgb(e['positivo'])}", f"ForegroundVisited={rgb(e['visitado'])}", ""]
        if grupo == "Header":
            lin += ["[Colors:Header][Inactive]", f"BackgroundAlternate={rgb(alterno)}",
                    f"BackgroundNormal={rgb(e['fondos']['Window'][0])}", f"DecorationFocus={rgb(e['acento'])}",
                    f"DecorationHover={rgb(e['acento_hover'])}", f"ForegroundActive={rgb(e['acento'])}",
                    f"ForegroundInactive={rgb(e['inactivo'])}", f"ForegroundLink={rgb(e['enlace'])}",
                    f"ForegroundNegative={rgb(e['negativo'])}", f"ForegroundNeutral={rgb(e['neutro'])}",
                    f"ForegroundNormal={rgb(e['texto'])}", f"ForegroundPositive={rgb(e['positivo'])}",
                    f"ForegroundVisited={rgb(e['visitado'])}", ""]
    a_bg, a_fg, i_bg, i_fg = e["wm"]
    lin += ["[WM]", f"activeBackground={rgb(a_bg)}", f"activeBlend={rgb(a_fg)}", f"activeForeground={rgb(a_fg)}",
            f"inactiveBackground={rgb(i_bg)}", f"inactiveBlend={rgb(i_fg)}", f"inactiveForeground={rgb(i_fg)}", ""]
    if oscuro:
        lin.insert(lin.index("[KDE]"), "")
    return "\n".join(lin)


def main():
    salida = Path(sys.argv[1]) if len(sys.argv) > 1 else SALIDA
    salida.mkdir(parents=True, exist_ok=True)
    for clave, e in ESQUEMAS.items():
        (salida / f"{clave}.colors").write_text(esquema(clave, e), encoding="utf-8")
        print(salida / f"{clave}.colors")


if __name__ == "__main__":
    main()
