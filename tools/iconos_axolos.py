#!/usr/bin/env python3
"""Tema de iconos "AxolOS": Yaru morado oscuro + iconos Yaru para las apps de KDE.

Uso: iconos_axolos.py SALIDA_DIR

Yaru-purple-dark no trae iconos de aplicaciones, así que Dolphin, Konsole,
Preferencias… salían de Breeze (otro estilo y otros colores). Este tema hereda
Yaru-purple-dark y añade enlaces con el nombre de cada app de KDE apuntando a
su equivalente Yaru (la variante morada si existe). Son enlaces simbólicos a
/usr/share/icons: no se copia ningún dibujo.
"""
import colorsys
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ICONS = Path("/usr/share/icons")
SOURCES = ["Yaru-purple", "Yaru"]           # primero la variante morada
MAP = {
    "org.kde.dolphin": ["nautilus", "org.gnome.Nautilus"],
    "system-file-manager": ["nautilus", "org.gnome.Nautilus"],
    "org.kde.konsole": ["utilities-terminal", "org.gnome.Terminal"],
    "utilities-terminal": ["utilities-terminal"],
    "systemsettings": ["org.gnome.Settings", "preferences-system"],
    "preferences-system": ["org.gnome.Settings", "preferences-system"],
    "org.kde.discover": ["org.gnome.Software", "software-store", "system-software-install"],
    "plasmadiscover": ["org.gnome.Software", "software-store", "system-software-install"],
    "org.kde.kate": ["org.gnome.TextEditor", "text-editor"],
    "org.kde.kwrite": ["org.gnome.TextEditor", "text-editor"],
    "org.kde.spectacle": ["org.gnome.Screenshot", "applets-screenshooter"],
    "org.kde.okular": ["org.gnome.Evince", "document-viewer"],
    "org.kde.gwenview": ["org.gnome.Loupe", "eog"],
    "org.kde.ark": ["org.gnome.FileRoller"],
    "org.kde.kcalc": ["accessories-calculator", "org.gnome.Calculator"],
    "org.kde.plasma-systemmonitor": ["org.gnome.SystemMonitor", "utilities-system-monitor"],
    "help-browser": ["help-browser", "org.gnome.Yelp"],
    "org.kde.khelpcenter": ["help-browser", "org.gnome.Yelp"],
}


def _hsv(rgb):
    r, g, b = [rgb[..., i] for i in range(3)]
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = np.where(mx - mn == 0, 1e-6, mx - mn)
    h = np.select([mx == r, mx == g], [((g - b) / d) % 6, (b - r) / d + 2], (r - g) / d + 4) / 6
    s = np.where(mx == 0, 0, (mx - mn) / np.maximum(mx, 1e-6))
    return h, s, mx


def is_blue(path):
    a = np.asarray(Image.open(path).convert("RGBA"), np.float32) / 255
    h, s, v = _hsv(a[..., :3])
    m = (a[..., 3] > 0.5) & (s > 0.35) & (v > 0.25)
    if m.sum() < 20:
        return False
    blue = m & (h > 190 / 360) & (h < 245 / 360)
    return blue.sum() / m.sum() > 0.25


def purple(src, dst):
    a = np.asarray(Image.open(src).convert("RGBA"), np.float32) / 255
    rgb = a[..., :3]
    h, s, v = _hsv(rgb)
    m = (s > 0.25) & (h > 190 / 360) & (h < 245 / 360)
    h2 = np.where(m, 250 / 360, h)
    # hsv → rgb
    i = np.floor(h2 * 6).astype(int) % 6
    f = h2 * 6 - np.floor(h2 * 6)
    p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
    out = np.choose(i[..., None].repeat(3, -1),
                    [np.dstack([v, t, p]), np.dstack([q, v, p]), np.dstack([p, v, t]),
                     np.dstack([p, q, v]), np.dstack([t, p, v]), np.dstack([v, p, q])])
    rgb = np.where(m[..., None], out, rgb)
    Image.fromarray((np.dstack([rgb, a[..., 3]]) * 255).round().astype(np.uint8), "RGBA").save(dst, optimize=True)


def size_dirs(theme):
    root = ICONS / theme
    return sorted(p.parent.relative_to(root) for p in root.glob("*/apps")) if root.is_dir() else []


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    dirs = set()
    made = {}
    for kde, cands in MAP.items():
        for size in sorted({d for t in SOURCES for d in size_dirs(t)}, key=str):
            for theme in SOURCES:
                hit = next((f for c in cands for f in (ICONS / theme / size / "apps").glob(f"{c}.*")
                            if f.name[: -len(f.suffix)] == c), None)
                if hit:
                    dst = out / size / "apps" / f"{kde}{hit.suffix}"
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    if dst.is_symlink() or dst.exists():
                        dst.unlink()
                    if hit.suffix == ".png" and is_blue(hit):
                        purple(hit, dst)            # azul de Yaru → morado AxolOS
                    else:
                        dst.symlink_to(hit)
                    dirs.add(str(size) + "/apps")
                    made[kde] = made.get(kde, 0) + 1
                    break
    lines = ["[Icon Theme]", "Name=AxolOS",
             "Comment=Yaru morado oscuro con iconos a juego para las apps de KDE",
             "Inherits=Yaru-purple-dark,Yaru-purple,Yaru,breeze-dark,breeze,hicolor",
             "Directories=" + ",".join(sorted(dirs)), ""]
    for d in sorted(dirs):
        name = d.split("/")[0]
        scale = 2 if name.endswith("@2x") else 1
        base = name.replace("@2x", "")
        lines += [f"[{d}]", "Context=Applications"]
        if base == "scalable":
            lines += ["Size=256", "MinSize=8", "MaxSize=512", "Type=Scalable"]
        else:
            lines += [f"Size={base.split('x')[0]}", f"Scale={scale}", "Type=Fixed"]
        lines.append("")
    (out / "index.theme").write_text("\n".join(lines), encoding="utf-8")
    print(f"Tema AxolOS: {len(made)} apps con icono Yaru, {len(dirs)} tamaños")
    for k in MAP:
        if k not in made:
            print("  sin equivalente:", k)


if __name__ == "__main__":
    main()
