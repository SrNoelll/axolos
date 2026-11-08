#!/usr/bin/env python3
"""Tema de Plasma "AxolOS": MacTahoe-Dark con todos sus azules (los de serie de
Breeze, #3daee9…) pasados al morado de las carpetas. Afecta al brillo del
borde del dock oculto, deslizadores, barras, campos de texto, OSD, etc.

Uso: plasma_axolos.py DIR_MacTahoe-Dark DIR_SALIDA
"""
import gzip
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kvantum_axolos import HEX, shift  # misma regla de color que el tema Kvantum AxolOS


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(src, out)
    changed = 0
    for f in out.rglob("*"):
        if f.suffix not in (".svg", ".svgz"):
            continue
        raw = f.read_bytes()
        gz = f.suffix == ".svgz"
        text = (gzip.decompress(raw) if gz else raw).decode("utf-8")
        new = HEX.sub(shift, text)
        if new != text:
            data = new.encode("utf-8")
            f.write_bytes(gzip.compress(data, mtime=0) if gz else data)
            changed += 1
    meta = out / "metadata.json"
    m = json.loads(meta.read_text(encoding="utf-8"))
    k = m["KPlugin"]
    k["Id"] = k["Name"] = "AxolOS"
    k["Description"] = "MacTahoe-Dark (Vince Liuice) con el morado de AxolOS"
    for key in [x for x in k if re.match(r"(Name|Description)\[", x)]:
        del k[key]
    meta.write_text(json.dumps(m, indent=4, ensure_ascii=False), encoding="utf-8")
    old = out / "metadata.desktop"
    if old.exists():
        old.unlink()
    print(f"Tema de Plasma AxolOS: {changed} gráficos recoloreados → {out}")


if __name__ == "__main__":
    main()
