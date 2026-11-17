#!/usr/bin/env python3
"""AxolOS · barras de título de cristal (Aurorae), oscura y clara.

Parte de la decoración «AxolOS» (de MacTahoe) y la deja translúcida con desenfoque (el efecto Glass
de KWin pone la refracción y el irisado). Opacidad 0,82 = la del cuerpo de las ventanas con Kvantum
(reduce_window_opacity=18): barra y contenido parecen una sola lámina de cristal.
  AxolOS        oscura (por defecto): negro violáceo #121218
  AxolOS-Claro  clara: blanco azulado #eef2f7
Los botones (cerrar morado, etc.) no se tocan.

Uso: tools/decoracion_cristal.py [carpeta aurorae/themes]
"""
import json
import re
import shutil
import sys
from pathlib import Path

TEMAS = Path(__file__).resolve().parent.parent / "packages/axolos-themes/assets/aurorae/themes"
VARIANTES = {
    "AxolOS": {"fondo": "#121218", "opacidad": 0.82, "texto": "236,236,243", "texto_inactivo": "138,138,153",
               "nombre": "AxolOS", "descripcion": "AxolOS liquid glass window decorations (dark)"},
    "AxolOS-Claro": {"fondo": "#eef2f7", "opacidad": 0.86, "texto": "28,34,48", "texto_inactivo": "122,130,149",
                     "nombre": "AxolOS Claro", "descripcion": "AxolOS liquid glass window decorations (light)"},
}


def main():
    temas = Path(sys.argv[1]) if len(sys.argv) > 1 else TEMAS
    base = temas / "AxolOS"
    original = (base / "decoration.svg").read_text(encoding="utf-8")
    # si ya se aplicó antes, se vuelve al gris del original para partir siempre de lo mismo
    original = re.sub(r"fill:#(121218|eef2f7);fill-opacity:0\.\d+", "fill:#242424;fill-opacity:1", original)
    rc_base = (base / "AxolOSrc").read_text(encoding="utf-8")
    meta_base = json.loads((base / "metadata.json").read_text(encoding="utf-8"))
    for nombre, v in VARIANTES.items():
        destino = temas / nombre
        if nombre != "AxolOS":
            shutil.rmtree(destino, ignore_errors=True)
            shutil.copytree(base, destino)
            (destino / "AxolOSrc").unlink()
        svg = original.replace("fill:#242424;fill-opacity:1", f"fill:{v['fondo']};fill-opacity:{v['opacidad']}")
        (destino / "decoration.svg").write_text(svg, encoding="utf-8")
        rc = rc_base
        for clave, valor in (("ActiveTextColor", v["texto"]), ("InactiveTextColor", v["texto_inactivo"]),
                             ("UseTextShadow", "false"), ("Blur", "true")):
            rc = re.sub(rf"^{clave}=.*$", f"{clave}={valor}", rc, flags=re.M)
        (destino / f"{nombre}rc").write_text(rc, encoding="utf-8")
        meta = json.loads(json.dumps(meta_base))
        meta["KPlugin"].update({"Name": v["nombre"], "Id": nombre, "Description": v["descripcion"]})
        meta["X-KDE-PluginInfo-blur"] = True
        if "X-KDE-PluginInfo-blur" in meta["KPlugin"]:
            meta["KPlugin"]["X-KDE-PluginInfo-blur"] = True
        (destino / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
        desk = destino / "metadata.desktop"
        if desk.exists():
            t = desk.read_text(encoding="utf-8")
            t = re.sub(r"^Name=.*$", f"Name={v['nombre']}", t, flags=re.M)
            t = re.sub(r"^X-KDE-PluginInfo-Name=.*$", f"X-KDE-PluginInfo-Name={nombre}", t, flags=re.M)
            desk.write_text(t, encoding="utf-8")
        print(destino)


if __name__ == "__main__":
    main()
