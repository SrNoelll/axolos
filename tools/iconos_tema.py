#!/usr/bin/env python3
"""AxolOS · índices de los temas de iconos (oscuro y claro).

«AxolOS» lleva los iconos de cristal (apps y carpetas, tools/iconos_cristal.py) y hereda Yaru morado
oscuro para todo lo demás. «AxolOS-Claro» tiene los MISMOS iconos (enlaces relativos a las carpetas
de AxolOS, no copias) pero hereda las variantes claras: los iconos de las barras de herramientas
(nueva pestaña, copiar, buscar…) salen oscuros y se ven sobre el cristal claro. Lo usa el tema
global claro; con el oscuro, en modo claro esos iconos salían blancos sobre blanco.

Uso: tools/iconos_tema.py [carpeta de temas de iconos]   (por defecto, la del paquete axolos-themes)
"""
import sys
from pathlib import Path

ICONOS = Path(__file__).resolve().parent.parent / "packages/axolos-themes/assets/icons"

TEMAS = {
    "AxolOS": ("AxolOS", "AxolOS liquid glass icons on top of Yaru purple",
               "Yaru-purple-dark,Yaru-purple,Yaru,breeze-dark,breeze,hicolor"),
    "AxolOS-Claro": ("AxolOS Light", "AxolOS liquid glass icons on top of Yaru purple, for the light mode",
                     # breeze primero: Yaru-purple hereda Yaru, cuyo «cerrar» es rojo (en oscuro sale de breeze-dark)
                     "breeze,Yaru-purple,Yaru,hicolor"),
}
CONTEXTO = {"apps": "Applications", "places": "Places"}


def carpetas(base):
    """Subcarpetas «tamaño/contexto» que existen en el tema AxolOS."""
    res = []
    def orden(p):                                     # 16x16, 16x16@2x, 24x24… 256x256@2x
        return int(p.name.split("x")[0]), p.name.endswith("@2x")
    for tam in sorted((p for p in base.iterdir() if p.is_dir() and not p.is_symlink()), key=orden):
        for ctx in sorted(c for c in tam.iterdir() if c.is_dir()):
            res.append(f"{tam.name}/{ctx.name}")
    return res


def indice(nombre, comentario, hereda, dirs):
    lineas = ["[Icon Theme]", f"Name={nombre}", f"Comment={comentario}", f"Inherits={hereda}",
              "Directories=" + ",".join(dirs), ""]
    for d in dirs:
        tam, ctx = d.split("/")
        escala = 2 if tam.endswith("@2x") else 1
        lado = tam.replace("@2x", "").split("x")[0]
        lineas += [f"[{d}]", f"Context={CONTEXTO.get(ctx, ctx.capitalize())}", f"Size={lado}",
                   f"Scale={escala}", "Type=Fixed", ""]
    return "\n".join(lineas)


def main():
    raiz = Path(sys.argv[1]) if len(sys.argv) > 1 else ICONOS
    base = raiz / "AxolOS"
    dirs = carpetas(base)
    for carpeta, (nombre, comentario, hereda) in TEMAS.items():
        destino = raiz / carpeta
        destino.mkdir(exist_ok=True)
        if carpeta != "AxolOS":
            for tam in dict.fromkeys(d.split("/")[0] for d in dirs):
                enlace = destino / tam
                if enlace.is_symlink():
                    enlace.unlink()
                enlace.symlink_to(Path("..") / "AxolOS" / tam)
        (destino / "index.theme").write_text(indice(nombre, comentario, hereda, dirs), encoding="utf-8")
        print(destino / "index.theme")


if __name__ == "__main__":
    main()
