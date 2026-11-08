#!/usr/bin/env python3
"""Paleta de terminal AxolOS: genera el esquema y el perfil de Konsole.

Uso: terminal_axolos.py SALIDA_DIR   → AxolOS.colorscheme y AxolOS.profile
Fondo grafito, texto claro, morado AxolOS como protagonista y colores ANSI
suaves pero distinguibles (la paleta de pywal del fondo salía toda gris).
"""
import sys
from pathlib import Path

#            normal        intenso       (nombre)
ANSI = [
    ("#1c1c22", "#4b4b57"),   # negro
    ("#ff7a93", "#ff9fb0"),   # rojo (rosa)
    ("#7ddfb4", "#a8efcf"),   # verde
    ("#f3cf7a", "#fbe2a6"),   # amarillo
    ("#8f85f2", "#b4acff"),   # azul → morado azulado
    ("#a69afe", "#cdc6ff"),   # magenta → morado AxolOS
    ("#7fd4e4", "#a9e6f1"),   # cian
    ("#c9c9d3", "#f3f3f8"),   # blanco
]
BG, BG_INT, FG, FG_INT = "#0f0f13", "#17171d", "#e6e6ee", "#ffffff"


def rgb(h):
    h = h.lstrip("#")
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def faint(h, k=0.66):
    h = h.lstrip("#")
    return ",".join(str(round(int(h[i:i + 2], 16) * k)) for i in (0, 2, 4))


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    L = []
    L += ["[Background]", f"Color={rgb(BG)}", "", "[BackgroundIntense]", f"Color={rgb(BG_INT)}", "",
          "[BackgroundFaint]", f"Color={rgb(BG)}", ""]
    for i, (n, b) in enumerate(ANSI):
        L += [f"[Color{i}]", f"Color={rgb(n)}", "", f"[Color{i}Intense]", f"Color={rgb(b)}", "",
              f"[Color{i}Faint]", f"Color={faint(n)}", ""]
    L += ["[Foreground]", f"Color={rgb(FG)}", "", "[ForegroundIntense]", f"Color={rgb(FG_INT)}", "",
          "[ForegroundFaint]", f"Color={faint(FG)}", "",
          "[General]", "Blur=false", "ColorRandomization=false", "Description=AxolOS",
          "FillStyle=Tile", "Opacity=1", "Wallpaper=", "WallpaperFlipType=NoFlip", "WallpaperOpacity=1", ""]
    (out / "AxolOS.colorscheme").write_text("\n".join(L), encoding="utf-8")
    (out / "AxolOS.profile").write_text("\n".join([
        "[Appearance]", "ColorScheme=AxolOS", "Font=JetBrainsMono Nerd Font,11,-1,5,400,0,0,0,0,0,0,0,0,0,0,1",
        "LineSpacing=1", "",
        "[Cursor Options]", "CursorShape=1", "UseCustomCursorColor=true",
        f"CustomCursorColor={rgb('#a69afe')}", f"CustomCursorTextColor={rgb(BG)}", "",
        "[General]", "Name=AxolOS", "Parent=FALLBACK/", "TerminalMargin=12", "TerminalCenter=false", "",
        "[Scrolling]", "ScrollBarPosition=2", ""]), encoding="utf-8")
    print("Konsole: AxolOS.colorscheme y AxolOS.profile en", out)


if __name__ == "__main__":
    main()
