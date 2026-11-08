#!/usr/bin/env python3
"""Crea el tema Kvantum "AxolOS": MacTahoe oscuro con los azules cambiados al
morado de las carpetas Yaru-purple-dark.

Uso: kvantum_axolos.py DIR_MacTahoe DIR_SALIDA

- Toma MacTahoeDark.kvconfig / MacTahoeDark.svg.
- Todo color azul (tono 190°–245°, con saturación) pasa al tono del morado de
  las carpetas (250°), conservando su luminosidad y saturación: así los
  contrastes del tema original se mantienen.
- El color de destacado se fija exacto al morado de las carpetas (#A69AFE).
- Escribe AxolOS.* y AxolOSDark.* (el estilo "kvantum-dark" busca <tema>Dark).
"""
import colorsys
import re
import sys
from pathlib import Path

FOLDER = "#a69afe"        # cuerpo de la carpeta Yaru-purple-dark (medido)
TARGET_HUE = 250 / 360.0  # tono de ese morado
HEX = re.compile(r"#([0-9a-fA-F]{6})\b")


def shift(m):
    h = m.group(1)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
    if 190 / 360 <= hh <= 245 / 360 and ss > 0.25 and 0.08 < ll < 0.95:
        # se acerca a la luminosidad de los morados de las carpetas (#9485ED / #A69AFE)
        ll = ll + (0.72 - ll) * 0.45 if ll < 0.72 else ll
        r, g, b = colorsys.hls_to_rgb(TARGET_HUE, ll, min(1.0, ss))
        return "#%02x%02x%02x" % tuple(round(c * 255) for c in (r, g, b))
    return m.group(0)


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    svg = HEX.sub(shift, (src / "MacTahoeDark.svg").read_text(encoding="utf-8"))
    cfg = HEX.sub(shift, (src / "MacTahoeDark.kvconfig").read_text(encoding="utf-8"))
    for key in ("highlight.color", "inactive.highlight.color"):
        cfg = re.sub(rf"^{re.escape(key)}=.*$", f"{key}={FOLDER}", cfg, flags=re.M)
    cfg = re.sub(r"^link\.color=.*$", f"link.color={FOLDER}", cfg, flags=re.M)
    for name in ("AxolOS", "AxolOSDark"):
        (out / f"{name}.svg").write_text(svg, encoding="utf-8")
        (out / f"{name}.kvconfig").write_text(cfg, encoding="utf-8")
    changed = sorted(set(HEX.findall((src / "MacTahoeDark.svg").read_text())) ^ set(HEX.findall(svg)))
    print(f"Tema Kvantum AxolOS creado en {out} ({len(changed)} colores distintos)")


if __name__ == "__main__":
    main()
